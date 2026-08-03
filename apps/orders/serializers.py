from rest_framework import serializers
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem, Payment, Coupon


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.ImageField(source="product.main_image", read_only=True)
    unit_price = serializers.DecimalField(source="product.effective_price", max_digits=10, decimal_places=2, read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "product_image", "unit_price", "quantity", "saved_for_later", "line_total"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    coupon_code = serializers.CharField(source="coupon.code", read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "subtotal", "discount", "coupon_code"]


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "unit_price", "quantity", "line_total"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "reference", "amount", "currency", "is_verified", "paid_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "customer", "full_name", "phone", "email",
            "delivery_address", "fulfilment_type", "special_instructions",
            "subtotal", "delivery_fee", "tax", "discount", "grand_total",
            "status", "payment_status", "items", "payment", "created_at",
        ]
        read_only_fields = ["order_number", "customer", "status", "payment_status", "created_at"]


class CheckoutSerializer(serializers.Serializer):
    """Validates checkout input and turns the customer's cart into an Order."""
    full_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    delivery_address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    fulfilment_type = serializers.ChoiceField(choices=Order.FulfilmentType.choices)
    special_instructions = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["fulfilment_type"] == Order.FulfilmentType.DELIVERY and not attrs.get("delivery_address"):
            raise serializers.ValidationError({"delivery_address": "Required for delivery orders."})
        return attrs

    @transaction.atomic
    def create_order_from_cart(self, cart: Cart, website_settings):
        items = cart.items.filter(saved_for_later=False)
        if not items.exists():
            raise serializers.ValidationError("Cart is empty.")

        subtotal = cart.subtotal
        discount = cart.discount
        delivery_fee = website_settings.delivery_fee if self.validated_data["fulfilment_type"] == "delivery" else 0
        if website_settings.min_order_for_free_delivery and subtotal >= website_settings.min_order_for_free_delivery:
            delivery_fee = 0
        tax = (subtotal - discount) * (website_settings.tax_percent / 100)
        grand_total = subtotal - discount + delivery_fee + tax

        order = Order.objects.create(
            customer=self.context["request"].user if self.context["request"].user.is_authenticated else None,
            full_name=self.validated_data["full_name"],
            phone=self.validated_data["phone"],
            email=self.validated_data["email"],
            delivery_address=self.validated_data.get("delivery_address", ""),
            fulfilment_type=self.validated_data["fulfilment_type"],
            special_instructions=self.validated_data.get("special_instructions", ""),
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            tax=tax,
            discount=discount,
            grand_total=grand_total,
            coupon=cart.coupon,
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                unit_price=item.product.effective_price,
                quantity=item.quantity,
            )
        if cart.coupon:
            cart.coupon.times_used += 1
            cart.coupon.save(update_fields=["times_used"])
        items.delete()
        return order
