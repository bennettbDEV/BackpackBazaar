from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["location", "image"]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "profile"]
        extra_kwargs = {"password": {"write_only": True}}

    def to_representation(self, instance):
        """Customize the serialized response to include nested profile data."""
        representation = super().to_representation(instance)
        if hasattr(instance, "profile"):
            representation["profile"] = UserProfileSerializer(instance.profile).data
        return representation
