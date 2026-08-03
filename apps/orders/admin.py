from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Payment, Coupon


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "status", "payment_status", "grand_total", "created_at")
    list_filter = ("status", "payment_status")
    inlines = [OrderItemInline]


admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Payment)
admin.site.register(Coupon)
