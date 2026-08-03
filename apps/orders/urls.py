from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CartView, ApplyCouponView, CheckoutView, VerifyPaymentView,
    OrderViewSet, DashboardStatsView,
)

router = DefaultRouter()
router.register("all", OrderViewSet, basename="order")

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/apply-coupon/", ApplyCouponView.as_view(), name="apply-coupon"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("payments/verify/", VerifyPaymentView.as_view(), name="verify-payment"),
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
] + router.urls
