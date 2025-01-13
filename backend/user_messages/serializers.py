from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "content", "edited_at", "edited", "sender", "receiver"]
        read_only_fields = [
            "edited_at",
            "edited",
            "sender",
        ]