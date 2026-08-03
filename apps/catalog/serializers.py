from rest_framework import serializers
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source="products.count", read_only=True)

    class Meta:
        model = Category
        fields = [
            "id", "name", "slug", "description", "image",
            "is_active", "display_order", "product_count",
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "display_order"]


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "category", "category_name", "short_description",
            "price", "discount_price", "effective_price", "main_image",
            "is_available", "is_featured", "spicy_level", "tags",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True
    )
    gallery_images = ProductImageSerializer(many=True, read_only=True)
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    tag_list = serializers.ListField(child=serializers.CharField(), read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "category", "category_id", "description", "short_description",
            "price", "discount_price", "effective_price", "main_image", "gallery_images",
            "stock_quantity", "is_available", "is_featured", "is_hidden", "is_out_of_stock",
            "preparation_time", "calories", "spicy_level", "tags", "tag_list",
            "created_at", "updated_at",
        ]
