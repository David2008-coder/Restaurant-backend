from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "customer", "name", "rating", "comment", "status", "is_featured", "created_at"]
        read_only_fields = ["id", "customer", "status", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        if request.user.is_authenticated:
            validated_data["customer"] = request.user
        return super().create(validated_data)
