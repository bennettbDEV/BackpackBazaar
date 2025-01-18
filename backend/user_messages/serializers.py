from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "content",
            "created_at",
            "edited_at",
            "edited",
            "related_listing",
            "sender",
            "receiver",
        ]
        read_only_fields = [
            "created_at",
            "edited_at",
            "edited",
            "sender",
        ]
