import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from .models import Listing, Tag
from .serializers import ListingSerializer


class ListingBaseTestCase(APITestCase):
    """Base test class providing setup for listing-related tests."""

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.client.force_authenticate(user=cls.user)

        cls.test_image = cls._retrieve_test_image()

        # Create example tags
        cls.tag1 = Tag.objects.create(tag_name="Tag1")
        cls.tag2 = Tag.objects.create(tag_name="Tag2")

        # Listing data template
        cls.valid_listing_data = {
            "title": "Sample Listing",
            "condition": "MW",
            "description": "A sample description.",
            "price": 101.0,
            "tags": ["Tag1", "Tag2"],
        }
        cls.valid_listing_data["image"] = cls.test_image

        cls.listing = Listing.objects.create(
            title="Sample Listing 0",
            condition="FN",
            description="A sample description.",
            price=100.0,
            image=cls.test_image,
            author_id=cls.user,
        )
        cls.listing.tags.set([cls.tag1, cls.tag2])

    @classmethod
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


class CreateListingTestCase(ListingBaseTestCase):
    def test_create_valid_listing(self):
        response = self.client.post(
            reverse("listing-list"), self.valid_listing_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Listing.objects.count(), 2)

    def test_create_listing_unauthenticated(self):
        self.client.logout()
        response = self.client.post(
            reverse("listing-list"), self.valid_listing_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RetrieveListingTestCase(ListingBaseTestCase):
    def test_retrieve_listing(self):
        response = self.client.get(
            reverse("listing-detail", kwargs={"pk": self.listing.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.listing.title)


class PartialUpdateListingTestCase(ListingBaseTestCase):
    def test_partial_update_listing(self):
        response = self.client.patch(
            reverse("listing-detail", kwargs={"pk": self.listing.pk}),
            {"description": "Updated description."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.description, "Updated description.")

    def test_update_listing_invalid_data(self):
        response = self.client.patch(
            reverse("listing-detail", kwargs={"pk": self.listing.pk}),
            {"price": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteListingTestCase(ListingBaseTestCase):
    def test_delete_listing(self):
        response = self.client.delete(
            reverse("listing-detail", kwargs={"pk": self.listing.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Listing.objects.filter(pk=self.listing.pk).exists())


class ListAndFilterListingsTestCase(ListingBaseTestCase):
    def test_list_listings(self):
        response = self.client.get(reverse("listing-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_listings_by_condition(self):
        response = self.client.get(reverse("listing-list") + "?condition=FN")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_listings(self):
        response = self.client.get(reverse("listing-list") + "?search=Sample")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_listings_by_price(self):
        Listing.objects.create(
            title="Another Listing",
            condition="MW",
            description="Another sample.",
            price=50.0,
            image=self.test_image,
            author_id=self.user,
        )
        response = self.client.get(reverse("listing-list") + "?ordering=price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)