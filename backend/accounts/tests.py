from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from accounts.models import UserBlock
from accounts.models import UserProfile


# Base class with common setup
class BaseUserTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create two users; user1 is the primary authenticated user
        self.user1 = User.objects.create_user(
            username="user1", password="password123", email="user1@example.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password123", email="user2@example.com"
        )
        # Force authentication for user1 for endpoints that require it
        self.client.force_authenticate(user=self.user1)


class CreateAccountTestCase(BaseUserTestCase):
    def test_create_account(self):  # With email
        # We should be unauthenticated to simulate new user
        self.client.logout()
        url = reverse("user-list")
        data = {
            "username": "newuser",
            "password": "newpassword123",
            "email": "newuser@example.com",
            "location": "Test Location",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that JWT tokens are returned in the response
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


class UpdateAccountTestCase(BaseUserTestCase):
    def test_update_account_basic(self):
        url = reverse("user-detail", kwargs={"pk": self.user1.pk})
        data = {"username": "updated_user1", "password": "password1234"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Reload from DB and check that user was updated successfully
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, "updated_user1")

    def test_update_account_basic_partial(self):
        url = reverse("user-detail", kwargs={"pk": self.user1.pk})
        data = {"location": "Partially Updated Location"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.profile.location, "Partially Updated Location")

    def test_update_account_partial(self):
        url = reverse("user-detail", kwargs={"pk": self.user1.pk})
        data = {
            "username": "updated_user1",
            "email": "newuseremail@example.com",
            "location": "Partially Updated Location",
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, "updated_user1")
        self.assertEqual(self.user1.email, "newuseremail@example.com")
        self.assertEqual(self.user1.profile.location, "Partially Updated Location")

    def test_update_other_account_partial(self):
        # Log into user2 then try and update user1
        self.client.logout()
        self.client.force_authenticate(user=self.user2)

        url = reverse("user-detail", kwargs={"pk": self.user1.pk})
        data = {
            "username": "updated_user1",
            "email": "newuseremail@example.com",
            "location": "Partially Updated Location",
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteAccountTestCase(BaseUserTestCase):
    def test_delete_account(self):
        url = reverse("user-detail", kwargs={"pk": self.user1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user1.pk).exists())

    def test_delete_account_unauthenticated(self):
        self.client.logout()
        url = reverse("user-detail", kwargs={"pk": self.user1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(User.objects.filter(pk=self.user1.pk).exists())

    def test_delete_other_account(self):
        # Log into user2 then try and delete user1
        self.client.logout()
        self.client.force_authenticate(user=self.user2)
        url = reverse("user-detail", kwargs={"pk": self.user1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(User.objects.filter(pk=self.user1.pk).exists())


class BlockUserTestCase(BaseUserTestCase):
    def test_block_user_success(self):
        url = reverse("user-block-user", kwargs={"pk": self.user2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserBlock.objects.filter(user=self.user1, blocked_user=self.user2).exists()
        )

    def test_block_self_failure(self):
        url = reverse("user-block-user", kwargs={"pk": self.user1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_block_user_already_blocked(self):
        url = reverse("user-block-user", kwargs={"pk": self.user2.pk})
        self.client.post(url)  # First block attempt
        response = self.client.post(url)  # Second attempt
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UnblockUserTestCase(BaseUserTestCase):
    def test_unblock_user_success(self):
        # First block user2
        block_url = reverse("user-block-user", kwargs={"pk": self.user2.pk})
        block_response = self.client.post(block_url)
        self.assertEqual(block_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserBlock.objects.filter(user=self.user1, blocked_user=self.user2).exists()
        )

        # Now unblock user2
        unblock_url = reverse("user-unblock-user", kwargs={"pk": self.user2.pk})
        response = self.client.post(unblock_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            UserBlock.objects.filter(user=self.user1, blocked_user=self.user2).exists()
        )

    def test_unblock_user_not_blocked(self):
        unblock_url = reverse("user-unblock-user", kwargs={"pk": self.user2.pk})
        response = self.client.post(unblock_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class IsUserBlockedTestCase(BaseUserTestCase):
    def test_is_user_blocked_true(self):
        # First block user2
        block_url = reverse("user-block-user", kwargs={"pk": self.user2.pk})
        block_response = self.client.post(block_url)
        self.assertEqual(block_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserBlock.objects.filter(user=self.user1, blocked_user=self.user2).exists()
        )

        # Not test if user2 is blocked
        url = reverse("user-is-user-blocked", kwargs={"pk": self.user2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("User is blocked", response.data.get("detail", ""))

    def test_is_user_blocked_false(self):
        url = reverse("user-is-user-blocked", kwargs={"pk": self.user2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("User is not blocked", response.data.get("detail", ""))


class ListBlockedUsersTestCase(BaseUserTestCase):
    def test_list_blocked_users(self):
        # Block user2 and verify that list returns it
        block_url = reverse("user-block-user", kwargs={"pk": self.user2.pk})
        block_response = self.client.post(block_url)
        self.assertEqual(block_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserBlock.objects.filter(user=self.user1, blocked_user=self.user2).exists()
        )

        url = reverse("user-list-blocked-users")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        blocked_ids = [user["id"] for user in response.data]
        self.assertIn(self.user2.pk, blocked_ids)
