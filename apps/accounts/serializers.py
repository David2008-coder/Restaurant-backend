from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomerProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "phone", "password", "password_confirm"]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        CustomerProfile.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    total_orders = serializers.IntegerField(source="profile.total_orders", read_only=True)
    total_spent = serializers.DecimalField(source="profile.total_spent", max_digits=12, decimal_places=2, read_only=True)
    address = serializers.CharField(source="profile.address", required=False)

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name", "phone",
            "role", "is_email_verified", "date_joined", "address",
            "total_orders", "total_spent",
        ]
        read_only_fields = ["id", "role", "is_email_verified", "date_joined"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        instance = super().update(instance, validated_data)
        if profile_data:
            CustomerProfile.objects.update_or_create(user=instance, defaults=profile_data)
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds user role/name to the JWT payload so the frontend can branch
    between customer and admin experiences without an extra request."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["name"] = user.get_full_name() or user.username
        token["is_admin"] = user.is_admin
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
