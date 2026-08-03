from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user. `role` drives Role-Based Access on top of Django's
    built-in is_staff/is_superuser for the admin dashboard."""

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_staff


class CustomerProfile(models.Model):
    """Extra profile data kept separate from auth so User stays lean."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True, default="Lagos")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.user.email}"

    @property
    def total_orders(self):
        return self.user.orders.count()

    @property
    def total_spent(self):
        from django.db.models import Sum
        total = self.user.orders.filter(payment_status="paid").aggregate(s=Sum("grand_total"))["s"]
        return total or 0
