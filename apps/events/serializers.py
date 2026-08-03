from rest_framework import serializers
from .models import Event, Booking


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id", "customer", "name", "phone", "email", "guests",
            "date", "time", "special_request", "status", "created_at",
        ]
        read_only_fields = ["id", "customer", "status", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        if request.user.is_authenticated:
            validated_data["customer"] = request.user
        return super().create(validated_data)
