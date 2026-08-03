from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "rating", "status", "is_featured", "created_at")
    list_filter = ("status", "rating")
