from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CustomerProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "role", "is_staff", "date_joined")
    fieldsets = BaseUserAdmin.fieldsets + (("Role", {"fields": ("role", "phone", "is_email_verified")}),)


admin.site.register(CustomerProfile)
