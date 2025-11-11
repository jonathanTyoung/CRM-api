# api/tests.py

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

# To run tests: pipenv run python manage.py test api

class AuthTests(APITestCase):
    """Tests for authentication-related endpoints: register, login, and current_user."""

    def setUp(self):
        """
        This method runs before each test.
        It sets up common URLs and sample user data for testing.
        """
        # Reverse resolves the URL names to actual paths
        self.register_url = reverse('register_user')
        self.login_url = reverse('login_user')
        self.current_user_url = reverse('current_user')

        # Sample user data used in registration and login
        self.user_data = {
            "username": "tester",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
            "email": "tester@example.com"
        }

    def test_register_user(self):
        """Test that a user can register successfully."""
        response = self.client.post(self.register_url, self.user_data, format='json')

        # Assert the request succeeded
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the response includes JWT tokens
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Assert the returned user matches the one we created
        self.assertEqual(response.data['user']['username'], self.user_data['username'])

    def test_login_user(self):
        """Test that a user can login successfully."""
        # First, create the user in the test database
        User.objects.create_user(**self.user_data)

        # Attempt login
        response = self.client.post(self.login_url, {
            "username": self.user_data['username'],
            "password": self.user_data['password']
        }, format='json')

        # Assert login succeeded and tokens are returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_current_user_requires_auth(self):
        """Test that current_user endpoint requires authentication and returns user data if authenticated."""
        # Create the user
        User.objects.create_user(**self.user_data)

        # Login to get access token
        login_response = self.client.post(self.login_url, {
            "username": self.user_data['username'],
            "password": self.user_data['password']
        }, format='json')
        access_token = login_response.data['access']

        # Set authorization header for the client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Access protected endpoint
        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check returned user data
        self.assertEqual(response.data['username'], self.user_data['username'])

    def test_current_user_without_auth(self):
        """Test that current_user endpoint rejects unauthenticated requests."""
        # No credentials set, should return 401
        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
