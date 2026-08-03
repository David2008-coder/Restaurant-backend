from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    class SpicyLevel(models.IntegerChoices):
        NONE = 0, "Not Spicy"
        MILD = 1, "Mild"
        MEDIUM = 2, "Medium"
        HOT = 3, "Hot"
        EXTRA_HOT = 4, "Extra Hot"

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=255, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    main_image = models.ImageField(upload_to="products/")
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")

    stock_quantity = models.PositiveIntegerField(default=100)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    preparation_time = models.PositiveIntegerField(default=20, help_text="Minutes")
    calories = models.PositiveIntegerField(null=True, blank=True)
    spicy_level = models.IntegerField(choices=SpicyLevel.choices, default=SpicyLevel.MEDIUM)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "name"]
        indexes = [models.Index(fields=["is_available", "is_hidden"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, i = base, 1
            while Product.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def effective_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def is_out_of_stock(self):
        return self.stock_quantity <= 0

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class ProductImage(models.Model):
    """Extra gallery images per product, beyond main_image."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.product.name} image #{self.pk}"
