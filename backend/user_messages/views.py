from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Message
from .serializers import MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show messages where user is the sender or receiver
        return Message.objects.filter(
            sender=self.request.user
        ) | Message.objects.filter(receiver=self.request.user)

    def perform_create(self, serializer):
        # Set sender to currently authenticated user
        serializer.save(sender=self.request.user)

    def perform_update(self, serializer):
        # Only the sender can modify their message
        if self.get_object().sender != self.request.user:
            raise PermissionDenied("You are not allowed to edit this message.")
        # When message is updated, set updated to true
        serializer.save(edited=True)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        if message.sender != request.user:
            raise PermissionDenied("You are not allowed to delete this message.")
        return super().destroy(request, *args, **kwargs)
