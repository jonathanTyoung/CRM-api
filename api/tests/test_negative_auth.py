from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User


class AuthNegativeTests(APITestCase):
    """Negative and edge-case tests for authentication."""

    def setUp(self):
        self.register_url = reverse('register_user')
        self.login_url = reverse('login_user')
        self.current_user_url = reverse('current_user')

        self.valid_data = {
            "email": "tester@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User"
        }

        # Create a real user for login tests
        self.user = User.objects.create_user(
            username=self.valid_data["email"],
            email=self.valid_data["email"],
            password=self.valid_data["password"],
            first_name="Test",
            last_name="User"
        )

    # --------------------------
    # REGISTRATION NEGATIVE TESTS
    # --------------------------

    def test_register_missing_email(self):
        payload = self.valid_data.copy()
        payload.pop("email")

        res = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_password(self):
        payload = self.valid_data.copy()
        payload.pop("password")

        res = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_first_name(self):
        payload = self.valid_data.copy()
        payload.pop("first_name")

        res = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """Registering an email that already exists should return 400."""
        res = self.client.post(self.register_url, self.valid_data, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", res.data)
        self.assertEqual(res.data["detail"], "Email already exists.")



    # --------------------------
    # LOGIN NEGATIVE TESTS
    # --------------------------

    def test_login_nonexistent_user(self):
        res = self.client.post(self.login_url, {
            "email": "ghost@example.com",
            "password": "doesntmatter"
        }, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_wrong_password(self):
        res = self.client.post(self.login_url, {
            "email": self.valid_data["email"],
            "password": "wrongpassword"
        }, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_email(self):
        res = self.client.post(self.login_url, {
            "password": self.valid_data["password"]
        }, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password(self):
        res = self.client.post(self.login_url, {
            "email": self.valid_data["email"]
        }, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_payload(self):
        res = self.client.post(self.login_url, {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # --------------------------
    # TOKEN / AUTH HEADER TESTS
    # --------------------------

    def test_current_user_invalid_token_format(self):
        """Invalid token format should be rejected."""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.here")

        res = self.client.get(self.current_user_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_no_bearer_prefix(self):
        """Missing 'Bearer' prefix should fail."""
        self.client.credentials(HTTP_AUTHORIZATION="InvalidPrefix abc123")

        res = self.client.get(self.current_user_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_empty_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer ")

        res = self.client.get(self.current_user_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------------
    # EXPIRED TOKEN TEST (OPTIONAL)
    # --------------------------

    def test_current_user_expired_token(self):
        """
        Placeholder test.
        To implement this properly, generate a token with a past 'exp'.
        Keeping as 401 expectation for now.
        """
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # fake
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired_token}")

        res = self.client.get(self.current_user_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
