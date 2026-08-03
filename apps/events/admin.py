from django.contrib import admin
from .models import Event, Booking

admin.site.register(Event)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date", "time", "guests", "status")
    list_filter = ("status", "date")
