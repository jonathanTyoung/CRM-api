from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import AgentProfile


class AgentProfileTests(APITestCase):
    """Tests ensuring agent profiles are auto-created."""

    def setUp(self):
        self.register_url = reverse("register_user")

        self.user_data = {
            "email": "agent@example.com",
            "password": "testpassword",
            "first_name": "Agent",
            "last_name": "Test"
        }

    def test_agent_profile_created_on_register(self):
        """When a user registers, an AgentProfile should be created automatically."""
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(email=self.user_data["email"])

        # Test via Django reverse relationship
        self.assertTrue(hasattr(user, "agent_profile"))

        profile = user.agent_profile
        self.assertEqual(profile.user, user)
