from django.contrib.auth.models import User
from django.db import models
from listings.models import Listing


class Message(models.Model):
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)

    # If the related listing is deleted, set reference to -1 to indicate it no longer exists
    related_listing = models.ForeignKey(
        Listing, on_delete=models.SET(-1), related_name="related_messages"
    )
    # Tentative "on_delete=models.CASCADE" - should messages stay after user is deleted?
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
