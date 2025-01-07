from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from .models import Listing, Tag
from .serializers import ListingSerializer


class ListingViewSetTests(APITestCase):
    def _generate_test_image(self):
        img = Image.new(
            "RGB", (100, 100), color=(255, 0, 0)
        )  # Create a 100x100 red image
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        return SimpleUploadedFile(
            "test_image.jpg", buffer.read(), content_type="image/jpeg"
        )

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)
        self.test_image = self._generate_test_image()

        # Create tag objects
        tag1 = Tag.objects.create(tag_name="Tag1")
        tag2 = Tag.objects.create(tag_name="Tag2")
        self.valid_listing_data = {
            "title": "Sample Listing",
            "condition": "MW",
            "description": "A sample description.",
            "price": 101.0,
            "tags": ["Tag1", "Tag2"],
        }
        self.valid_listing_data["image"] = self._generate_test_image()

        self.listing = Listing.objects.create(
            title="Sample Listing 0",
            condition="FN",
            description="A sample description.",
            price=100.0,
            image=self.test_image,
            author_id=self.user,
        )
        self.listing.tags.set([tag1, tag2])

    def test_create_valid_listing(self):
        url = reverse("listing-list")
        response = self.client.post(
            url, data=self.valid_listing_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Listing.objects.count(), 2)
        self.assertIn("Tag1", [tag.tag_name for tag in Tag.objects.all()])

    def test_create_listing_unauthenticated(self):
        self.client.logout()
        self.valid_listing_data["image"] = self._generate_test_image()
        url = reverse("listing-list")
        response = self.client.post(
            url, data=self.valid_listing_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_listing(self):
        response = self.client.get(
            reverse("listing-detail", kwargs={"pk": self.listing.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.listing.title)

    def test_update_listing(self):
        updated_data = self.valid_listing_data.copy()
        updated_data["description"] = "Updated description."
        response = self.client.put(
            reverse("listing-detail", kwargs={"pk": self.listing.pk}),
            updated_data,
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.description, "Updated description.")

    def test_delete_listing(self):
        response = self.client.delete(
            reverse("listing-detail", kwargs={"pk": self.listing.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Listing.objects.filter(pk=self.listing.pk).exists())

    def test_list_listings(self):
        response = self.client.get(reverse("listing-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), Listing.objects.count())

    def test_filter_listings_by_condition(self):
        response = self.client.get(reverse("listing-list") + "?condition=FN")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(item["condition"] == "FN" for item in response.data["results"])
        )

    def test_search_listings(self):
        response = self.client.get(reverse("listing-list") + "?search=Sample")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any("Sample" in item["title"] for item in response.data["results"])
        )

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
        self.assertEqual(response.data["results"][0]["price"], 50.0)
