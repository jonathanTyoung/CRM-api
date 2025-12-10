from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import AgentProfile


class AuthTests(APITestCase):
    """Secure, real-world authentication tests for registration, login, and current_user."""

    def setUp(self):
        self.register_url = reverse("register_user")
        self.login_url = reverse("login_user")
        self.current_user_url = reverse("current_user")

        self.user_data = {
            "email": "tester@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
        }

        # Create a user for login tests
        self.user = User.objects.create_user(
            username=self.user_data["email"],
            email=self.user_data["email"],
            password=self.user_data["password"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
        )
        self.user.refresh_from_db()  # Ensure AgentProfile exists

    # ----------------------------------------------------------------------
    # REGISTRATION TESTS
    # ----------------------------------------------------------------------

    def test_register_success(self):
        payload = {
            "email": "new@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
        }

        res = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

        created = User.objects.get(email=payload["email"])
        self.assertTrue(AgentProfile.objects.filter(user=created).exists())

    def test_register_duplicate_email(self):
        res = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data["detail"], "Email already exists.")

    def test_register_missing_fields(self):
        res = self.client.post(self.register_url, {}, format="json")
        self.assertEqual(res.status_code, 400)

    # ----------------------------------------------------------------------
    # LOGIN TESTS
    # ----------------------------------------------------------------------

    def test_login_success(self):
        res = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }, format="json")

        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)

    def test_login_wrong_password(self):
        res = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": "wrongpass"
        }, format="json")

        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data["detail"], "Invalid email or password.")

    def test_login_nonexistent_user(self):
        res = self.client.post(self.login_url, {
            "email": "ghost@example.com",
            "password": "irrelevant"
        }, format="json")

        self.assertEqual(res.status_code, 401)

    def test_login_missing_email(self):
        res = self.client.post(self.login_url, {"password": "x"}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_login_missing_password(self):
        res = self.client.post(self.login_url, {"email": "x@example.com"}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_login_empty_payload(self):
        res = self.client.post(self.login_url, {}, format="json")
        self.assertEqual(res.status_code, 400)

    # ----------------------------------------------------------------------
    # CURRENT USER TESTS
    # ----------------------------------------------------------------------

    def authenticate(self):
        """Helper to login and set Authorization header."""
        res = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }, format="json")

        token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_current_user_success(self):
        self.authenticate()
        res = self.client.get(self.current_user_url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertIn("agent_profile_id", res.data)

    def test_current_user_requires_auth(self):
        res = self.client.get(self.current_user_url)
        self.assertEqual(res.status_code, 401)

    def test_current_user_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.here")
        res = self.client.get(self.current_user_url)
        self.assertEqual(res.status_code, 401)

    def test_current_user_missing_bearer(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token abc123")
        res = self.client.get(self.current_user_url)
        self.assertEqual(res.status_code, 401)

    def test_current_user_empty_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer ")
        res = self.client.get(self.current_user_url)
        self.assertEqual(res.status_code, 401)
