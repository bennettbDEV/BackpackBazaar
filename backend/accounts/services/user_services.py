from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction

from accounts.models import UserProfile


class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(username, password, email="", profile=None):
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
        )
        if profile:
            UserProfile.objects.create(
                user=user,
                location=profile.get("location"),
                image=profile.get("image"),
            )
        else:
            UserProfile.objects.create(
                user=user,
                location="",
                image=None,
            )
        return user

    @staticmethod
    @transaction.atomic
    def update_user(user_id, username=None, email=None, password=None, profile=None):
        user = User.objects.get(id=user_id)
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = make_password(password)
        user.save()

        # If explicit profile with extra data is added - save the new profile data
        if profile:
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            if "location" in profile:
                user_profile.location = profile["location"]
            if "image" in profile:
                user_profile.image = profile["image"]
            user_profile.save()

        return user

    @staticmethod
    @transaction.atomic
    def delete_user(user_id):
        user = User.objects.get(id=user_id)
        user.delete()