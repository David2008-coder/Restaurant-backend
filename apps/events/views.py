from rest_framework import viewsets, permissions
from apps.common.permissions import IsAdminOrReadOnly
from apps.common.utils import log_activity
from .models import Event, Booking
from .serializers import EventSerializer, BookingSerializer


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering_fields = ["event_date"]

    def get_queryset(self):
        qs = Event.objects.all()
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "orders"

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Booking.objects.all()
        if user.is_authenticated:
            return Booking.objects.filter(customer=user)
        return Booking.objects.none()

    def perform_create(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "created reservation", instance, guests=instance.guests)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, f"set booking status to {instance.status}", instance)
