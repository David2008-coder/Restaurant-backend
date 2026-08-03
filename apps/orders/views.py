import uuid
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsAdminOrReadOnly
from apps.common.utils import log_activity
from apps.content.models import WebsiteSettings
from .models import Cart, CartItem, Order, Coupon
from .serializers import CartSerializer, OrderSerializer, CheckoutSerializer
from . import paystack


def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        return cart
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, customer=None)
    return cart


class CartView(APIView):
    """A single resource-oriented endpoint for the customer's own cart —
    simpler for the frontend than a full ViewSet for a singleton object."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = _get_or_create_cart(request)
        return Response(CartSerializer(cart).data)

    def post(self, request):
        """Add or update an item: { product: id, quantity: int }"""
        cart = _get_or_create_cart(request)
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))
        item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id, defaults={"quantity": quantity})
        if not created:
            item.quantity = quantity if request.data.get("set_exact") else item.quantity + quantity
            item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        cart = _get_or_create_cart(request)
        item_id = request.data.get("item_id")
        CartItem.objects.filter(cart=cart, id=item_id).delete()
        return Response(CartSerializer(cart).data)


class ApplyCouponView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        cart = _get_or_create_cart(request)
        code = request.data.get("code", "").strip()
        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True)
        except Coupon.DoesNotExist:
            return Response({"detail": "Invalid or expired coupon."}, status=400)
        now = timezone.now()
        if coupon.valid_until and coupon.valid_until < now:
            return Response({"detail": "Coupon has expired."}, status=400)
        if coupon.usage_limit and coupon.times_used >= coupon.usage_limit:
            return Response({"detail": "Coupon usage limit reached."}, status=400)
        cart.coupon = coupon
        cart.save()
        return Response(CartSerializer(cart).data)


class CheckoutView(APIView):
    """Cart -> Order, then hands back a Paystack authorization URL to redirect to."""
    permission_classes = [permissions.AllowAny]
    throttle_scope = "orders"

    def post(self, request):
        settings_obj, _ = WebsiteSettings.objects.get_or_create(pk=1)
        cart = _get_or_create_cart(request)
        serializer = CheckoutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.create_order_from_cart(cart, settings_obj)

        reference = f"IGW-{uuid.uuid4().hex[:10]}"
        paystack_data = paystack.initialize_transaction(
            email=order.email,
            amount_naira=order.grand_total,
            reference=reference,
            callback_url=request.data.get("callback_url", ""),
        )
        from .models import Payment
        Payment.objects.create(order=order, reference=reference, amount=order.grand_total)

        return Response({
            "order": OrderSerializer(order).data,
            "authorization_url": paystack_data.get("data", {}).get("authorization_url"),
            "reference": reference,
        }, status=status.HTTP_201_CREATED)


class VerifyPaymentView(APIView):
    """Called by the frontend after Paystack's popup/redirect closes.
    Independently re-verifies with Paystack before marking the order paid —
    never trust the client-side callback alone."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from .models import Payment
        reference = request.data.get("reference")
        payment = generics.get_object_or_404(Payment, reference=reference)
        result = paystack.verify_transaction(reference)
        data = result.get("data", {})

        payment.raw_response = result
        if data.get("status") == "success":
            payment.is_verified = True
            payment.paid_at = timezone.now()
            payment.save()
            payment.order.payment_status = Order.PaymentStatus.PAID
            payment.order.status = Order.OrderStatus.ACCEPTED
            payment.order.save()
            log_activity(None, "payment verified", payment.order, reference=reference)
            return Response({"status": "success", "order": OrderSerializer(payment.order).data})

        payment.order.payment_status = Order.PaymentStatus.FAILED
        payment.order.save()
        payment.save()
        return Response({"status": "failed"}, status=400)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "payment_status"]
    search_fields = ["order_number", "full_name", "phone"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, f"set order status to {instance.status}", instance)


class DashboardStatsView(APIView):
    """Powers the admin Dashboard Home screen in one call."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        week_start = today - timedelta(days=7)
        month_start = today - timedelta(days=30)

        paid = Order.objects.filter(payment_status=Order.PaymentStatus.PAID)

        def revenue_since(date):
            return paid.filter(created_at__date__gte=date).aggregate(s=Sum("grand_total"))["s"] or 0

        orders_today = Order.objects.filter(created_at__date=today)

        from apps.events.models import Booking
        from apps.catalog.models import Product

        return Response({
            "today_orders": orders_today.count(),
            "today_revenue": revenue_since(today),
            "weekly_revenue": revenue_since(week_start),
            "monthly_revenue": revenue_since(month_start),
            "pending_orders": Order.objects.filter(status=Order.OrderStatus.PENDING).count(),
            "completed_orders": Order.objects.filter(status=Order.OrderStatus.COMPLETED).count(),
            "cancelled_orders": Order.objects.filter(status=Order.OrderStatus.CANCELLED).count(),
            "reservations_today": Booking.objects.filter(date=today).count(),
            "low_stock_products": list(
                Product.objects.filter(stock_quantity__lte=5, is_hidden=False)
                .values("id", "name", "stock_quantity")[:10]
            ),
            "popular_products": list(
                OrderItemPopularity()
            ),
            "recent_orders": OrderSerializer(Order.objects.all()[:8], many=True).data,
        })


def OrderItemPopularity():
    from .models import OrderItem
    qs = (
        OrderItem.objects.values("product__id", "product__name")
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")[:6]
    )
    return [{"product_id": r["product__id"], "name": r["product__name"], "total_sold": r["total_sold"]} for r in qs]
