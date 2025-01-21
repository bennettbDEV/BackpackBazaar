from django.contrib.auth.models import User
from django.db import models
from django.db.models import Case, F, Max, Q, When
from listings.models import Listing
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Message
from .serializers import MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    pagination_class = None  # temporary
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # If not performing list action, queryset should be any message that involves the user
        if self.action != "list":
            return Message.objects.filter(Q(sender=user) | Q(receiver=user))

        # Show most recent message for each unique (reciever, related_listing) pair
        latest_messages = (
            Message.objects.filter(
                Q(sender=self.request.user) | Q(receiver=self.request.user)
            )
            .annotate(
                # Normalize the sender, reciever id order, so we dont retrieve multiple messages for the same conversation
                # Ex. ids (sender=5, receiver=3, related_listing=1) would retrieve a message
                # and ids (sender=3, receiver=5, related_listing=1) would retrieve a message from same convo - which we dont want
                # Thus the order will always be (a,b) where a<b
                user_one=Case(
                    When(sender__lt=F("receiver"), then=F("sender")),
                    default=F("receiver"),
                ),
                user_two=Case(
                    When(sender__lt=F("receiver"), then=F("receiver")),
                    default=F("sender"),
                ),
            )
            # Group by related_related listing_id and sender_id (or reciever_id)
            .values("related_listing", "user_one", "user_two")
            # Save id for the newest message in each distinct group
            .annotate(latest_message_id=Max("id"))
            # Create a list of all the collected message ids
            .values_list("latest_message_id", flat=True)
        )

        return (
            # Filter ids that we collected above
            Message.objects.filter(id__in=latest_messages)
            .select_related("sender", "receiver", "related_listing")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        # Set sender to currently authenticated user
        serializer.save(sender=self.request.user)

    def update(self, request, *args, **kwargs):
        # Extract only message content from request data
        partial_data = {"content": request.data.get("content")}
        if "content" not in request.data or len(request.data) > 1:
            raise PermissionDenied("Only the 'content' field can be updated.")

        # Update message manually
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=partial_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

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
