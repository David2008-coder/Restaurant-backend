from django.db import models


class HeroSection(models.Model):
    """Only one active hero at a time — the homepage always pulls the active row."""
    heading = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    image = models.ImageField(upload_to="hero/")
    background_video = models.FileField(upload_to="hero/video/", blank=True, null=True)
    button_text = models.CharField(max_length=60, default="See the Menu")
    button_link = models.CharField(max_length=200, default="/menu")
    promo_banner_text = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            HeroSection.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.heading


class GalleryImage(models.Model):
    image = models.ImageField(upload_to="gallery/")
    caption = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.caption or f"Gallery image #{self.pk}"


class HomepageSection(models.Model):
    """Generic editable block (About teaser, Story block, CTA strip, etc.)
    so new homepage content doesn't require a code change."""
    key = models.SlugField(max_length=80, unique=True)
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to="homepage/", blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.key


class WebsiteSettings(models.Model):
    """Singleton-style settings row (site name, currency, delivery fee, tax)."""
    site_name = models.CharField(max_length=120, default="Itagokwaife Grillspot")
    tagline = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    currency_symbol = models.CharField(max_length=5, default="₦")
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=1500)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=7.5)
    min_order_for_free_delivery = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    maintenance_mode = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.site_name


class ContactInformation(models.Model):
    address = models.CharField(max_length=255, default="Lagos, Nigeria")
    phone_primary = models.CharField(max_length=30, blank=True)
    phone_secondary = models.CharField(max_length=30, blank=True)
    whatsapp_number = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    google_maps_embed_url = models.URLField(blank=True)
    opening_hours = models.JSONField(
        default=dict, blank=True,
        help_text='e.g. {"mon_fri": "11:00 - 23:00", "sat_sun": "11:00 - 00:00"}'
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Contact Information"


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]
        verbose_name = "FAQ"

    def __str__(self):
        return self.question


class Testimonial(models.Model):
    customer_name = models.CharField(max_length=120)
    quote = models.TextField()
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.customer_name
