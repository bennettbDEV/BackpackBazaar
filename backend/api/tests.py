# api/tests.py
import os
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from api.handlers import ListingHandler, UserHandler
from api.models import Listing, User
from api.serializers import ListingSerializer, LoginSerializer, UserSerializer
from api.views import ListingViewSet
from config.settings import BASE_DIR


# Functions/Classes to help setup Tests
class AuthenticatedAPITestCase(APITestCase):
    """Helper class that is used to turn the APIClient into an authenicated client for testing purposes.

    Extends APITestCase from Django Rest Framework which includes helpful logic used for HTTP requests.

    Attributes:
        client (APIClient): The client object that is used to perform HTTP methods to the test server.
    """

    def setUp(self):
        self.user_handler = UserHandler()

        data = {
            "username": "TestUsername",
            "password": "TestPassword",
        }
        serializer = UserSerializer(data=data)
        response = None

        # Create test user
        if serializer.is_valid():
            response = self.user_handler.register_user(serializer.validated_data)
        else:
            print(serializer.errors)
            return

        # If test user exists for some reason, login instead
        if response.data.get("error") == "Username already exists.":
            login_serializer = LoginSerializer(
                data={"username": data["username"], "password": data["password"]}
            )

            if login_serializer.is_valid():
                response = self.user_handler.login(
                    user_data=login_serializer.validated_data
                )
            else:
                print(serializer.errors)
                return

        access_token = response.data["access"]
        status_code = response.status_code

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def tearDown(self):
        user = self.user_handler.get_user_by_username("TestUsername")
        url = reverse("user-detail", args=[user.id])
        response = self.client.delete(url)


class AuthenticatedListingAPITestCase(AuthenticatedAPITestCase):
    """Class with helper methods for listing creation and deletion for testing purposes.

    Extends AuthenticatedAPITestCase (APITestCase) which creates and deletes an authenticated
    user for use in testing - using the setUp() and tearDown() methods.

    Attributes:
        listing_handler (ListingHandler): A handler class that handles DB interactions related to listings.
        listing_list_url (String): The string representation of the URL path to list and create listings.
        listing_ids (List): The current list of created test listing ids. This is used for testing and during cleanup.
        client (APIClient): The authenticated client object that is used to perform HTTP methods to the test server.
    """

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

    def _create_test_listing(self, iteration, base_title, condition, price):
        test_image = self._generate_test_image()

        data = {
            "title": f"{base_title}{iteration}",
            "description": f"This is test description {iteration}.",
            "price": price,
            "image": test_image,
            "tags": ["Test", "Testing", "Development"],
            "condition": condition,
        }
        response = self.client.post(self.listing_list_url, data, format="multipart")
        return response

    def _create_test_listings(
        self, num_listings=1, base_title="TestListing", condition="Well Worn", price=10
    ):
        """Creates the specified number of test listings with an incrementing title.

        Args:
            num_listings (int, optional): The number of listings to be created. Defaults to 1.
            base_title (str, optional): The base string which is incremented: Example TestListing1, TestListing2. Defaults to "TestListing".
        """

        # Create test listings here
        # test_image = self._generate_test_image()

        for i in range(1, num_listings + 1):
            response = self._create_test_listing(i, base_title, condition, price)

            if response and response.status_code == 201:
                self.listing_ids.append(response.data.get("id"))
            elif response.data.get("image")[0] == "The submitted file is empty.":
                # Try again
                response = self._create_test_listing(i, base_title, condition, price)

                if response and response.status_code == 201:
                    self.listing_ids.append(response.data.get("id"))
                else:
                    print("Failed to create test listing")
                    print(response.data)
            else:
                print("Failed to create test listing")
                print(response.data)

    def _delete_test_listings(self):
        """Deletes all listings from self.listing_ids."""

        for listing_id in self.listing_ids:
            url = reverse("listing-detail", args=[listing_id])
            response = self.client.delete(url)

    # Before
    def setUp(self):
        # Authenticate client
        super().setUp()

        # Setup attributes for creating + deleting listings
        self.listing_handler = ListingHandler()
        self.listing_list_url = reverse("listing-list")
        self.listing_ids = []

    # After
    def tearDown(self):
        self._delete_test_listings()
        super().tearDown()


"""
Create Tests Here
"""


# Bennett test case 1:
# python manage.py test api.tests.ListListingsAPITestCase
@override_settings(MEDIA_ROOT=os.path.join(BASE_DIR, "tmp/test_media/"))
class ListListingsAPITestCase(AuthenticatedListingAPITestCase):
    """Unit tests for listing-list requests. Includes tests for Use case: Retrieve Listings.

    Extends AuthenticatedListingAPITestCase (AuthenticatedAPITestCase): which includes helper
    methods for listing creation and deletion for testing purposes.
    """

    # Before
    def setUp(self):
        super().setUp()

    # After
    def tearDown(self):
        super().tearDown()

    # Retrieve Listings Use case - test all retrieval methods -> including pagination
    def test_authenticated_get_listings(self):
        response = self.client.get(f"{self.listing_list_url}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data.get("results")), 0)

    def test_unauthenticated_get_listings(self):
        # Stop including any credentials
        self.client.credentials()  # Clears credentials

        response = self.client.get(f"{self.listing_list_url}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data.get("results")), 0)

    # This method should only be run in development env, never in prod because it deletes all listings
    def _test_empty_listings_response(self):
        # Ensure there are no listings in the database
        self.listing_handler.delete_all_listings()

        response = self.client.get(self.listing_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results", []), [])

    # Test pagination
    def test_valid_page_number(self):
        response = self.client.get(f"{self.listing_list_url}?page=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data.get("results")), 0)

    def test_too_large_page_number(self):
        response = self.client.get(f"{self.listing_list_url}?page=99999999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("detail"), "Invalid page.")

    def test_negative_page_number(self):
        response = self.client.get(f"{self.listing_list_url}?page=-2")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("detail"), "Invalid page.")

    def test_pagination(self):
        # Create enough listings to create 2 pages
        self._create_test_listings(15)

        # Request the first page
        response = self.client.get(f"{self.listing_list_url}?page=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 10)

        # Request the second page
        response = self.client.get(f"{self.listing_list_url}?page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data.get("results")), 5)

    # Test all sorting options
    def test_sorting_by_title_ascending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=title")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [field["title"] for field in response.data.get("results")]
        self.assertEqual(titles, sorted(titles))

    def test_sorting_by_title_descending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=-title")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [field["title"] for field in response.data.get("results")]
        self.assertEqual(titles, sorted(titles, reverse=True))

    def test_sorting_by_condition_ascending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=condition")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        conditions = [field["condition"] for field in response.data.get("results")]
        self.assertEqual(conditions, sorted(conditions))

    def test_sorting_by_condition_descending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=-condition")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        conditions = [field["condition"] for field in response.data.get("results")]
        self.assertEqual(conditions, sorted(conditions, reverse=True))

    def test_sorting_by_description_ascending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=description")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        descriptions = [field["description"] for field in response.data.get("results")]
        self.assertEqual(descriptions, sorted(descriptions))

    def test_sorting_by_description_descending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=-description")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        descriptions = [field["description"] for field in response.data.get("results")]
        self.assertEqual(descriptions, sorted(descriptions, reverse=True))

    def test_sorting_by_price_ascending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(field["price"]) for field in response.data.get("results")]
        self.assertEqual(prices, sorted(prices))

    def test_sorting_by_price_descending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=-price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(field["price"]) for field in response.data.get("results")]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_sorting_by_likes_ascending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=likes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        likes = [field["likes"] for field in response.data.get("results")]
        self.assertEqual(likes, sorted(likes))

    def test_sorting_by_likes_descending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=-likes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        likes = [field["likes"] for field in response.data.get("results")]
        self.assertEqual(likes, sorted(likes, reverse=True))

    def test_sorting_by_dislikes_ascending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=dislikes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dislikes = [field["dislikes"] for field in response.data.get("results")]
        self.assertEqual(dislikes, sorted(dislikes))

    def test_sorting_by_dislikes_descending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=-dislikes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dislikes = [field["dislikes"] for field in response.data.get("results")]
        self.assertEqual(dislikes, sorted(dislikes, reverse=True))

    def test_sorting_by_created_at_ascending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=created_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        created_at = [field["created_at"] for field in response.data.get("results")]
        self.assertEqual(created_at, sorted(created_at))

    def test_sorting_by_created_at_descending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=-created_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        created_at = [field["created_at"] for field in response.data.get("results")]
        self.assertEqual(created_at, sorted(created_at, reverse=True))

    def test_sorting_by_invalid_field_ascending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=author_id")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "Invalid ordering parameter.")

    def test_sorting_by_invalid_field_descending(self):
        response = self.client.get(f"{self.listing_list_url}?ordering=-author_id")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "Invalid ordering parameter.")


# Bennett test case 2a:
# python manage.py test api.tests.SearchListingsAPITestCase
@override_settings(MEDIA_ROOT=os.path.join(BASE_DIR, "tmp/test_media/"))
class SearchListingsAPITestCase(AuthenticatedListingAPITestCase):
    """Unit tests for searching listing-list requests. Includes tests for Use case: Search for Listings

    Extends AuthenticatedListingAPITestCase (AuthenticatedAPITestCase): which includes helper
    methods for listing creation and deletion for testing purposes.
    """

    # Before
    def setUp(self):
        super().setUp()

    # After
    def tearDown(self):
        super().tearDown()

    # Search for Listings Use case - Test searching possibilites
    def test_searching_valid_term(self):
        # Create 1 listing - which will be called Interesting textbook
        self._create_test_listings(1, base_title="Interesting Textbook")

        # Search for book:
        response = self.client.get(f"{self.listing_list_url}?search=book")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that all returned listings have 'book' in title, description, or tags
        self.assertTrue(
            all(
                "book"
                in (
                    listing.get("title", "").lower()
                    + listing.get("description", "").lower()
                    + " ".join(listing.get("tags", [])).lower()
                )
                for listing in response.data.get("results")
            )
        )

    def test_searching_invalid_term(self):
        # Create 1 listing - which will be called Interesting textbook
        self._create_test_listings(1, base_title="Interesting Textbook")

        # Search for insane term:
        response = self.client.get(
            f"{self.listing_list_url}?search=----------------$$$$$$$$$$$$$$$$$$$$_------------432756489125621657849653924......43.r..vf...fdsv..fd.v..r.vfds."
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that no listings have the given search term
        self.assertEqual(len(response.data.get("results")), 0)


# Bennett test case 2b:
# python manage.py test api.tests.FilterListingsAPITestCase
@override_settings(MEDIA_ROOT=os.path.join(BASE_DIR, "tmp/test_media/"))
class FilterListingsAPITestCase(AuthenticatedListingAPITestCase):
    """Unit tests for filtered listing-list requests. Includes tests for Use case: Filter Search Results

    Extends AuthenticatedListingAPITestCase (AuthenticatedAPITestCase): which includes helper
    methods for listing creation and deletion for testing purposes.
    """

    # Before
    def setUp(self):
        super().setUp()

    # After
    def tearDown(self):
        super().tearDown()

    # Filter Search Results Use case - Test all filtering options
    def test_filtering_by_condition_factory_new(self):
        # Create 1 listing - which will have "Factory New" as its condition
        self._create_test_listings(1, "TestListing", condition="Factory New")

        # Filter by condition
        response = self.client.get(f"{self.listing_list_url}?condition=Factory New")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(
                "Factory New" in listing.get("condition", "")
                for listing in response.data.get("results")
            )
        )

    def test_filtering_by_condition_minimal_wear(self):
        # Create 1 listing - which will have "Minimal Wear" as its condition
        self._create_test_listings(1, "TestListing", condition="Minimal Wear")

        # Filter by condition
        response = self.client.get(f"{self.listing_list_url}?condition=Minimal Wear")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(
                "Minimal Wear" in listing.get("condition", "")
                for listing in response.data.get("results")
            )
        )

    def test_filtering_by_condition_fair(self):
        # Create 1 listing - which will have "Fair" as its condition
        self._create_test_listings(1, "TestListing", condition="Fair")

        # Filter by condition
        response = self.client.get(f"{self.listing_list_url}?condition=Fair")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(
                "Fair" in listing.get("condition", "")
                for listing in response.data.get("results")
            )
        )

    def test_filtering_by_condition_well_worn(self):
        # Create 1 listing - which will have "Well Worn" as its condition
        self._create_test_listings(1, "TestListing", condition="Well Worn")

        # Filter by condition
        response = self.client.get(f"{self.listing_list_url}?condition=Well Worn")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(
                "Well Worn" in listing.get("condition", "")
                for listing in response.data.get("results")
            )
        )

    def test_filtering_by_condition_refurbished(self):
        # Create 1 listing - which will have "Refurbished" as its condition
        self._create_test_listings(1, "TestListing", condition="Refurbished")

        # Filter by condition
        response = self.client.get(f"{self.listing_list_url}?condition=Refurbished")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(
                "Refurbished" in listing.get("condition", "")
                for listing in response.data.get("results")
            )
        )

    def test_filtering_by_valid_author_id(self):
        user = self.user_handler.get_user_by_username("TestUsername")

        # Create 5 listings - which will be made by the test user we retrieved above
        self._create_test_listings(5, "TestListing")

        # Assert that all of the retieved listings have author_id = the test users id
        response = self.client.get(f"{self.listing_list_url}?author_id={user.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(
                user.id == listing.get("author_id", "")
                for listing in response.data.get("results")
            )
        )

    def test_filtering_by_invalid_author_id(self):
        # Create 5 listings - which will be made by the test user we retrieved above
        self._create_test_listings(5, "TestListing")

        response = self.client.get(f"{self.listing_list_url}?author_id=-1")

        # Assert that there are no listings made by the user with author_id = -1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results", []), [])

    def test_filtering_by_min_price(self):
        # Create listings with varying prices
        self._create_test_listings(1, "TestListing", price=50)
        self._create_test_listings(1, "TestListing", price=50)
        self._create_test_listings(1, "TestListing", price=200)
        self._create_test_listings(1, "TestListing", price=250)

        # Filter by minimum price
        response = self.client.get(f"{self.listing_list_url}?min_price=200")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(
                listing.get("price", 0) >= 200
                for listing in response.data.get("results")
            )
        )

    def test_filtering_by_max_price(self):
        # Create listings with varying prices
        self._create_test_listings(1, "TestListing", price=50)
        self._create_test_listings(1, "TestListing", price=100)
        self._create_test_listings(1, "TestListing", price=300)
        self._create_test_listings(1, "TestListing", price=400)

        # Filter by maximum price
        response = self.client.get(f"{self.listing_list_url}?max_price=300")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(
                listing.get("price", 0) <= 300
                for listing in response.data.get("results")
            )
        )

    def test_filtering_by_min_likes(self):
        # Create listings
        self._create_test_listings(2, "TestListing")
        # like the listings

        # Filter by minimum likes
        response = self.client.get(f"{self.listing_list_url}?min_likes=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(
                listing.get("likes", 0) >= 2 for listing in response.data.get("results")
            )
        )

    def test_filtering_by_max_dislikes(self):
        # Create listings with varying dislike counts
        self._create_test_listings(2, "TestListing")
        # dislike the listings

        # Filter by maximum dislikes
        response = self.client.get(f"{self.listing_list_url}?max_dislikes=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(
                listing.get("dislikes", 0) <= 5
                for listing in response.data.get("results")
            )
        )

    def test_filtering_by_invalid_field(self):
        response = self.client.get(f"{self.listing_list_url}?free=True")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "Invalid parameter.")

    # These are basically integration tests as they make sure a newly created listing is present when retrieving listings
    def test_integrated_authenticated_get_listings(self):
        # Create 1 listing
        listing_title = "TestListing1"
        # Helper method will create 1 listing named TestListing1 based on the given parameters
        self._create_test_listings(1, "TestListing")

        found_listing = False
        page = 1
        max_pages = 100

        while page <= max_pages:
            # Construct the URL for the current page
            url = f"{self.listing_list_url}?page={page}"

            # Send GET request for current page
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Check if the listing on the current page
            if any(
                listing.get("title") == listing_title
                for listing in response.data.get("results")
            ):
                found_listing = True
                break

            # If no listing found and we have reached the last page, break
            # No "next" link means we are at the last page
            if not response.data.get("links").get("next"):
                break

            page += 1

        # Assert that the listing was found, return string with better description if not
        self.assertTrue(
            found_listing, f"{listing_title} was not found in any of the pages."
        )

    def test_integrated_unauthenticated_get_listings(self):
        # Create 1 listing
        listing_title = "TestListing1"
        # Helper method will create 1 listing named TestListing1 based on the given parameters
        self._create_test_listings(1, "TestListing")

        # Stop including any credentials
        self.client.credentials()

        found_listing = False
        page = 1
        max_pages = 100

        while page <= max_pages:
            # Construct the URL for the current page
            url = f"{self.listing_list_url}?page={page}"

            # Send GET request for current page
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Check if the listing on the current page
            if any(
                listing.get("title") == listing_title
                for listing in response.data.get("results")
            ):
                found_listing = True
                break

            # If no listing found and we have reached the last page, break
            # No "next" link means we are at the last page
            if not response.data.get("links").get("next"):
                break

            page += 1

        # Assert that the listing was found, return string with better description if not
        self.assertTrue(
            found_listing, f"{listing_title} was not found in any of the pages."
        )


"""
TEST CLASS: LikeListingTestCase
-Chase Test 1
-run:
python manage.py test api.tests.LikeListingTestCase.test_like_listing
python manage.py test api.tests.LikeListingTestCase.test_like_nonexistent_listing
python manage.py test api.tests.LikeListingTestCase.test_like_deleted_listing
"""
class LikeListingTestCase(AuthenticatedAPITestCase):
    # Function: setup a test image for a test listing
    def generate_test_image(self):
        img = Image.new(
            "RGB", (100, 100), color=(255, 0, 0)
        )  # Create a 100x100 red image
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        return SimpleUploadedFile(
            "test_image.jpg", buffer.read(), content_type="image/jpeg"
        )

    # Function: Set up the test environment
    def setUp(self):
        super().setUp()
        test_image = self.generate_test_image()
        # Create a test listing
        self.test_listing_data = {
            "title": "Test Listing",
            "condition": "New",
            "description": "A sample test listing for testing like functionality.",
            "image": test_image,
            "price": 999.0,
            "likes": 0,
            "dislikes": 0,
            "tags": ["Test", "Sample"],
        }
        # Retrieve the authenticated user's ID
        self.user_id = self.user_handler.get_user_by_username("TestUsername").id
        # Create the listing and retrieve its ID from the response
        response = ListingHandler().create_listing(
            validated_data=self.test_listing_data, user_id=self.user_id
        )
        assert response.status_code == 201, f"Failed to create listing: {response.data}"
        self.listing_id = response.data.get("id")
        assert (
            self.listing_id is not None
        ), "Listing ID was not returned in the response."
        # Define the like endpoint for the created listing
        self.like_url = reverse("listing-like-listing", kwargs={"pk": self.listing_id})

    # Function: delete this test data
    def tearDown(self):
        if self.listing_id:
            # Construct the endpoint for deleting the listing
            url = reverse("listing-detail", args=[self.listing_id])
            # Send a DELETE request using the authenticated client
            response = self.client.delete(url)
        # Call the parent teardown for user cleanup
        super().tearDown()

    """
    Unit Test Cases
    """

    # Case: a normal liking a listing and incrementing the like count.
    def test_like_listing(self):
        # Send a POST request to the like endpoint
        response = self.client.post(self.like_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            f"Expected status 204, got {response.status_code}.",
        )
        # Fetch the updated listing data to verify the like count
        updated_listing = ListingHandler().get_listing(self.listing_id)
        # Evaluate
        self.assertEqual(
            updated_listing.likes,
            1,
            f"Expected 1 like, got {updated_listing.likes}.",
        )

    # Case: liking a non-existent listing - expecting a 404
    def test_like_nonexistent_listing(self):
        # Create an invalid URL for a non-existent listing ID (-100)
        invalid_url = reverse("listing-like-listing", kwargs={"pk": -100})
        # Send a POST request to the invalid URL
        response = self.client.post(invalid_url)
        # Evaluate
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f"Expected status 404, got {response.status_code}.",
        )

    # Case: liking a listing that has been deleted - expecting a 404
    def test_like_deleted_listing(self):
        # Delete the existing test listing
        url = reverse("listing-detail", args=[self.listing_id])
        delete_response = self.client.delete(url)
        # Assert the listing was deleted successfully (status 204 or 200)
        self.assertIn(
            delete_response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK],
            f"Expected status 204 or 200 for delete, got {delete_response.status_code}.",
        )
        # Try liking the deleted listing
        response = self.client.post(self.like_url)
        # Evaluate the response status
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f"Expected status 404, got {response.status_code}.",
        )


"""
TEST CLASS: FavoriteListingTestCase
-Chase Test 2
-run:
python manage.py test api.tests.FavoriteListingTestCase.test_favorite_listing
python manage.py test api.tests.FavoriteListingTestCase.test_favorite_nonexistent_listing
python manage.py test api.tests.FavoriteListingTestCase.test_favorite_deleted_listing
"""
class FavoriteListingTestCase(AuthenticatedAPITestCase):
    # Function: setup a test image for a test listing
    def generate_test_image(self):
        img = Image.new(
            "RGB", (100, 100), color=(0, 255, 0)
        )  # Create a 100x100 green image
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        return SimpleUploadedFile(
            "test_favorite_image.jpg", buffer.read(), content_type="image/jpeg"
        )

    # Function: setup data (user and listing)
    def setUp(self):
        super().setUp()
        test_image = self.generate_test_image()

        # Create a test listing
        self.test_listing_data = {
            "title": "Favorite Listing",
            "condition": "New",
            "description": "A sample test listing for testing favorite functionality.",
            "image": test_image,
            "price": 599.0,
            "likes": 0,
            "dislikes": 0,
            "tags": ["Favorite", "Test"],
        }
        # Retrieve the authenticated user's ID
        self.user_id = self.user_handler.get_user_by_username("TestUsername").id
        # Create the listing and retrieve its ID from the response
        response = ListingHandler().create_listing(
            validated_data=self.test_listing_data, user_id=self.user_id
        )
        # Check that the response is successful and contains the listing ID
        assert response.status_code == 201, f"Failed to create listing: {response.data}"
        self.listing_id = response.data.get("id")
        assert (
            self.listing_id is not None
        ), "Listing ID was not returned in the response."
        # Define the favorite endpoint for the created listing
        self.favorite_url = reverse(
            "listing-favorite-listing", kwargs={"pk": self.listing_id}
        )

    # Function: deletes the test environment
    def tearDown(self):
        if hasattr(self, "listing_id") and self.listing_id:
            url = reverse("listing-detail", args=[self.listing_id])
            self.client.delete(url)
        super().tearDown()

    """
    Unit Test Cases
    """

    # Case: a normal favoriting of a listing
    def test_favorite_listing(self):
        # Send a POST request to the favorite endpoint
        response = self.client.post(self.favorite_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            f"Expected status 204, got {response.status_code}.",
        )
        favorite_entry = ListingViewSet.favorite_listing(self.user_id, self.listing_id)

        # Evaluate
        self.assertIsNotNone(
            favorite_entry, "The listing was not favorited by the user."
        )

    # Case: favoriting a non-existent listing
    def test_favorite_nonexistent_listing(self):
        # ensure listing does not exist
        invalid_url = reverse("listing-favorite-listing", kwargs={"pk": -100})
        response = self.client.post(invalid_url)
        # Evaluate
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f"Expected status 404, got {response.status_code}.",
        )

    # Case: favoriting a listing that has been deleted - expecting 404
    def test_favorite_deleted_listing(self):
        # Delete the listing
        url = reverse("listing-detail", args=[self.listing_id])
        delete_response = self.client.delete(url)
        # Assert that the listing was deleted successfully
        self.assertIn(
            delete_response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK],
            f"Expected status 204 or 200 for delete, got {delete_response.status_code}.",
        )
        # Try favoriting the deleted listing
        response = self.client.post(self.favorite_url)
        # Evaluate the response status
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f"Expected status 404, got {response.status_code}.",
        )


"""
TEST CLASS: Create Listing Testcase
-Jake Test Case 1
-run:
python manage.py test api.tests.CreateListingTestCase
"""
class CreateListingTestCase(AuthenticatedAPITestCase):
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
        super().setUp()
        test_img = self._generate_test_image()
        self.test_listing = {
            "title": "Test Listing",
            "condition": "Factory New",
            "description": "A sample test listing",
            "price": 999.0,
            "image": test_img,
            "tags": ["English", "Writing"],
        }
        self.user_id = self.user_handler.get_user_by_username("TestUsername").id

    # After
    def tearDown(self):
        super().tearDown()

    def test_create_valid_listing(self):
        url = reverse("listing-list")
        response = self.client.post(url, data=self.test_listing, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # validate other fields
        for key, value in self.test_listing.items():
            if key != "image":
                # assertEqual freaks out with the images, so not asserting it
                self.assertEqual(response.data.get(key), value)

    def test_create_invalid_listing(self):
        url = reverse("listing-list")
        # invalid due to missing values
        self.invalid_listing = {
            "condition": "Factory New",
            "description": "A sample test listing",
            "price": 999.0,
            "tags": ["English", "Writing"],
        }
        response = self.client.post(url, data=self.invalid_listing, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_listing_invalid_user(self):
        url = reverse("listing-detail", args=[9359318135135])
        response = self.client.post(url, data=self.test_listing, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


"""
TEST CLASS: Delete Listing Testcase
-Jake Test Case 2
-run:
python manage.py test api.tests.DeleteListingTestCase
"""
class DeleteListingTestCase(AuthenticatedAPITestCase):
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
        super().setUp()
        test_img = self._generate_test_image()
        self.test_listing = {
            "title": "Test Listing",
            "condition": "Factory New",
            "description": "A sample test listing",
            "price": 999.0,
            "image": test_img,
            "tags": ["English", "Writing"],
        }
        self.user_id = self.user_handler.get_user_by_username("TestUsername").id

    # After
    def tearDown(self):
        super().tearDown()

    def test_delete_valid_listing(self):
        # Create a Listing
        url = reverse("listing-list")
        response = self.client.post(url, data=self.test_listing, format="multipart")
        # Delete the Listing
        self.listing_id = response.data.get("id")
        url = reverse("listing-detail", args=[self.listing_id])
        response = self.client.delete(url)
        # Assert Equal
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_invalid_listing(self):
        # Create a Listing
        url = reverse("listing-list")
        response = self.client.post(url, data=self.test_listing, format="multipart")
        # Delete the Listing
        self.listing_id = response.data.get("id")
        url = reverse("listing-detail", args=[835838568])
        response = self.client.delete(url)
        # Assert Equal
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


"""
TEST CLASS: Dislike Listing Testcase
-Trevin Test Case 1
-run:
python manage.py test api.tests.DislikeListingTestCase
"""
class DislikeListingTestCase(AuthenticatedAPITestCase):
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

    def _create_test_listings(self, num_listings=1, base_title="TestListing"):
        """Creates the specified number of test listings with an incrementing title.

        Args:
            num_listings (int, optional): The number of listings to be created. Defaults to 1.
            base_title (str, optional): The base string which is incremented: Example TestListing1, TestListing2. Defaults to "TestListing".
        """

        # Create test listings here
        test_image = self._generate_test_image()

        for i in range(1, num_listings + 1):
            data = {
                "title": f"{base_title}{i}",
                "description": f"This is test description {i}.",
                "price": f"{i}{i}",
                "image": test_image,
                "tags": ["Test", "Testing", "Development"],
                "condition": "Well Worn",
            }
            response = self.client.post(
                self.list_listings_url, data, format="multipart"
            )
            if response and response.status_code == 201:
                self.listing_ids.append(response.data.get("id"))
            else:
                print(response.data)

    def _delete_test_listings(self):
        """Deletes all listings from self.listing_ids."""

        for listing_id in self.listing_ids:
            url = reverse("listing-detail", args=[listing_id])
            response = self.client.delete(url)

    # Before
    def setUp(self):
        super().setUp()
        self.listing_handler = ListingHandler()
        self.listing_ids = []
        self.list_listings_url = reverse("listing-list")
        self._create_test_listings(1)

    # After
    def tearDown(self):
        self._delete_test_listings()
        super().tearDown()

    def test_dislike_listing(self):
        # Send a POST request to the dislike endpoint
        self.dislike_url = reverse(
            "listing-dislike-listing", kwargs={"pk": self.listing_ids[0]}
        )
        response = self.client.post(self.dislike_url)
        # Verify the response status is 204 No Content (success)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            f"Expected status 204, got {response.status_code}.",
        )
        # Fetch the updated listing data to verify the like count
        updated_listing = ListingHandler().get_listing(self.listing_ids[0])
        # evaluate
        self.assertEqual(
            updated_listing.dislikes,
            1,
            f"Expected 1 like, got {updated_listing.dislikes}.",
        )

    def test_dislike_nonexistent_listing(self):
        invalid_url = reverse("listing-dislike-listing", kwargs={"pk": -21417926535879})
        response = self.client.post(invalid_url)
        # evaluate
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f"Expected status 404, got {response.status_code}.",
        )


"""
TEST CLASS: Retrieve Listing Testcase
-Trevin Test Case 2
-run:
python manage.py test api.tests.RetrieveListingTestCase
"""
class RetrieveListingTestCase(AuthenticatedAPITestCase):
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

    def _create_test_listings(self, num_listings=1, base_title="TestListing"):
        """Creates the specified number of test listings with an incrementing title.

        Args:
            num_listings (int, optional): The number of listings to be created. Defaults to 1.
            base_title (str, optional): The base string which is incremented: Example TestListing1, TestListing2. Defaults to "TestListing".
        """

        # Create test listings here
        test_image = self._generate_test_image()

        for i in range(1, num_listings + 1):
            data = {
                "title": f"{base_title}{i}",
                "description": f"This is test description {i}.",
                "price": f"{i}{i}",
                "image": test_image,
                "tags": ["Test", "Testing", "Development"],
                "condition": "Well Worn",
            }
            response = self.client.post(
                self.list_listings_url, data, format="multipart"
            )
            if response and response.status_code == 201:
                self.listing_ids.append(response.data.get("id"))
            else:
                print(response.data)

    def _delete_test_listings(self):
        """Deletes all listings from self.listing_ids."""

        for listing_id in self.listing_ids:
            url = reverse("listing-detail", args=[listing_id])
            response = self.client.delete(url)

    # setup function
    def setUp(self):
        # setup user using super class function
        super().setUp()
        test_image = self._generate_test_image()
        self.list_listings_url = reverse("listing-list")
        self.listing_ids = []

        # create a test listing
        self._create_test_listings(2)

        # define the listing endpoint for the created listing
        self.detail_listing_url = reverse("listing-detail", args=[self.listing_ids[0]])
        # we all good

    def test_retrieve_listing(self):
        # Send a POST request to the dislike endpoint
        response = self.client.get(self.detail_listing_url)
        # Verify the response status is 200(success)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f"Expected status 200, got {response.status_code}.",
        )
        # Make sure info from test listing is in retrieval

    def test_retrieve_nonexistant_listing(self):
        invalid_url = reverse("listing-detail", args=[-21417926535879])
        response = self.client.get(invalid_url)
        # evaluate
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f"Expected status 404, got {response.status_code}.",
        )

    def test_retrieve_deleted_listing(self):
        deletion_url = reverse("listing-detail", args=[self.listing_ids[0]])
        self.client.delete(deletion_url)

        # Try retrieving the deleted listing
        response = self.client.get(deletion_url)

        # Evaluate that its equal to what its supposed to
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f"Expected status 404, got {response.status_code}.",
        )

    # teardown function
    def tearDown(self):
        self._delete_test_listings()
        super().tearDown()
