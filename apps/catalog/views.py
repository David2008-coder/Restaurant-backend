from rest_framework import viewsets, permissions
from apps.common.permissions import IsAdminOrReadOnly
from apps.common.utils import log_activity
from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer, ProductImageSerializer,
)
from .filters import ProductFilter


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name", "description"]
    ordering_fields = ["display_order", "name"]

    def get_queryset(self):
        qs = Category.objects.all()
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "created category", instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "updated category", instance)


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "tags"]
    ordering_fields = ["price", "name", "created_at"]

    def get_queryset(self):
        qs = Product.objects.select_related("category").prefetch_related("gallery_images")
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_hidden=False)
        return qs

    def get_serializer_class(self):
        return ProductDetailSerializer if self.action in ("retrieve", "create", "update", "partial_update") else ProductListSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "created product", instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "updated product", instance)

    def perform_destroy(self, instance):
        log_activity(self.request.user, "deleted product", instance, name=instance.name)
        instance.delete()


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAdminUser]
