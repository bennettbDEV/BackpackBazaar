from django.contrib.auth.models import User
from django.db import models
from listings.models import Listing


class Message(models.Model):
    content = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)

    related_listing = models.ForeignKey(
        Listing, on_delete=models.SET_NULL, related_name="related_messages", null=True
    )
    # Tentative "on_delete=models.CASCADE" - should messages stay after user is deleted?
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
