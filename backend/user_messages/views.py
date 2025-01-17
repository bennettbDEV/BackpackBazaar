from django.contrib.auth.models import User
from django.db import models
from django.db.models import OuterRef, Subquery, Max
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Message
from listings.models import Listing
from .serializers import MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    pagination_class = None  # temporary
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Show most recent message for each unique (reciever, related_listing) pair
        latest_message_ids = (
            Message.objects.filter(
                sender=self.request.user,
                receiver=OuterRef("receiver"),
                related_listing=OuterRef("related_listing"),
            )
            .order_by("-created_at")  # Order by most recent
            .values("id")[:1]  # Take the most recent message ID
        )

        return (
            Message.objects.filter(id__in=Subquery(latest_message_ids))
            .select_related("receiver", "related_listing")
            .distinct()
        )

    def perform_create(self, serializer):
        # Set sender to currently authenticated user
        serializer.save(sender=self.request.user)

    def perform_update(self, serializer):
        # Only the sender can modify their message
        if self.get_object().sender != self.request.user:
            raise PermissionDenied("You are not allowed to edit this message.")

        # Only allow updates to content field
        if any(field for field in serializer.validated_data if field != "content"):
            raise PermissionDenied("Only the 'content' field can be updated.")

        # When message is updated, set updated to true
        serializer.save(edited=True)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        if message.sender != request.user:
            raise PermissionDenied("You are not allowed to delete this message.")
        return super().destroy(request, *args, **kwargs)

    # List messages between the current user and another user specified by user_id
    # Full url example: /messages/with_user/?user_id=1
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def with_user(self, request):
        user_id = request.query_params.get("user")
        listing_id = request.query_params.get("listing")

        if not user_id:
            return Response(
                {"error": "user parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not listing_id:
            return Response(
                {"error": "listing parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            other_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            related_listing = Listing.objects.get(pk=listing_id)
        except Listing.DoesNotExist:
            return Response(
                {"error": "Listing not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # models.Q used for more eloborate query
        # to retrieve all messages between specified users
        messages = Message.objects.filter(
            models.Q(related_listing=related_listing)
            & (
                (models.Q(sender=self.request.user) & models.Q(receiver=other_user))
                | (models.Q(sender=other_user) & models.Q(receiver=self.request.user))
            )
        ).order_by("created_at")

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
