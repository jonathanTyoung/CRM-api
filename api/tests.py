from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import AgentProfile


class AuthTests(APITestCase):
    """Tests for email-based authentication endpoints: register, login, and current_user."""

    def setUp(self):
        self.register_url = reverse('register_user')
        self.login_url = reverse('login_user')
        self.current_user_url = reverse('current_user')

        self.user_data = {
            "email": "tester@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User"
        }

    def test_register_user(self):
        """Ensure a user can register using email and password."""
        response = self.client.post(self.register_url, self.user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # User returned should match by email
        self.assertEqual(response.data['user']['email'], self.user_data['email'])

    def test_login_user(self):
        """Ensure a user can log in using email and password."""
        # Create user manually (email used as username)
        User.objects.create_user(
            username=self.user_data['email'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name']
        )

        response = self.client.post(self.login_url, {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_current_user_requires_auth(self):
        """Ensure current_user returns info only when authenticated."""
        User.objects.create_user(
            username=self.user_data['email'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )

        login_response = self.client.post(self.login_url, {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }, format='json')

        access = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])

    def test_current_user_without_auth(self):
        """Ensure unauthorized requests get rejected."""
        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_agent_profile_created_on_register(self):
        """Ensure an AgentProfile is automatically created when a user registers."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(email=self.user_data["email"])

        # Ensure profile exists via signals
        self.assertTrue(hasattr(user, "agent_profile"))

        profile = user.agent_profile
        self.assertEqual(profile.user, user)
