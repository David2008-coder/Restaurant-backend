from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "display_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_available", "is_featured", "stock_quantity")
    list_filter = ("category", "is_available", "is_featured")
    search_fields = ("name", "description")
    inlines = [ProductImageInline]
    prepopulated_fields = {"slug": ("name",)}
