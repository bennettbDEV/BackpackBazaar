from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    location = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="profile_images/", null=True, blank=True)

    def __str__(self):
        return self.user.username


class UserBlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocking")
    blocked_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blocked_by"
    )
    
