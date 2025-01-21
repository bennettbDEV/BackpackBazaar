import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from listings.models import Listing, Tag
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Message
from .serializers import MessageSerializer


class MessageBaseTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")

        # Create example listing so there is a listing to reference in messages
        self.listing_image = self._retrieve_test_image()
        self.tag1 = Tag.objects.create(tag_name="Tag1")
        self.tag2 = Tag.objects.create(tag_name="Tag2")

        self.listing = Listing.objects.create(
            title="Sample Listing 0",
            condition="FN",
            description="A sample description.",
            price=100.0,
            image=self.listing_image,
            author_id=self.user1,
        )
        self.listing.tags.set([self.tag1, self.tag2])

        self.message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            related_listing=self.listing,
            content="Hello from user1",
        )
        self.message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            related_listing=self.listing,
            content="Hello back from user2",
        )
        self.client.force_authenticate(user=self.user1)

    def _retrieve_test_image(cls):
        image_path = os.path.join(settings.BASE_DIR, "media", "tests", "test_image.jpg")
        # Only create image if it doesnt exist
        if not os.path.exists(image_path):
            img = Image.new("RGB", (100, 100), color=(255, 0, 0))
            img.save(image_path, format="JPEG")
        with open(image_path, "rb") as image_file:
            return SimpleUploadedFile(
                "test_image.jpg", image_file.read(), content_type="image/jpeg"
            )


class ListMessagesTestCase(MessageBaseTestCase):
    def test_get_message_list(self):
        response = self.client.get(reverse("message-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Add more specific logic later


class CreateMessageTestCase(MessageBaseTestCase):
    def test_create_message(self):
        data = {
            "receiver": self.user2.id,
            "related_listing": self.listing.id,
            "content": "This is the third message in our convo",
        }
        response = self.client.post(reverse("message-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 3)


class ListMessagesWithUserTestCase(MessageBaseTestCase):
    def test_with_user_action(self):
        url = reverse("message-with-user")
        response = self.client.get(
            url, {"user": self.user2.id, "listing": self.listing.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        messages = Message.objects.filter(
            related_listing=self.listing, sender=self.user1, receiver=self.user2
        ) | Message.objects.filter(
            related_listing=self.listing, sender=self.user2, receiver=self.user1
        )
        serializer = MessageSerializer(messages.order_by("created_at"), many=True)
        self.assertEqual(response.data, serializer.data)
