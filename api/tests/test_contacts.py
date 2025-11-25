from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import Contact, Source


class ContactTests(APITestCase):
    """Tests for Contact CRUD and permission rules."""

    def setUp(self):
        # Create agent user
        self.user = User.objects.create_user(
            username="agent1@example.com",
            email="agent1@example.com",
            password="testpassword"
        )

        # Login agent1
        login_res = self.client.post(reverse("login_user"), {
            "email": "agent1@example.com",
            "password": "testpassword"
        })
        token = login_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # other URLs
        self.list_url = reverse("contact-list")

        # Create source for payload
        self.source = Source.objects.create(name="Website")

        self.payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "555-1111",
            "source": self.source.id,
        }

    def test_create_contact(self):
        """Agent can create a contact"""
        res = self.client.post(self.list_url, self.payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["email"], "john@example.com")

        contact = Contact.objects.get(id=res.data["id"])
        self.assertEqual(contact.owner.user, self.user)

    def test_list_contacts(self):
        """Agent should see only their own contacts"""
        # Create a contact for agent1
        self.client.post(self.list_url, self.payload, format="json")

        # Create agent2 + contact owned by agent2
        agent2 = User.objects.create_user(
            username="agent2@example.com",
            email="agent2@example.com",
            password="testpassword"
        )

        # Login agent2 to create a contact
        login2 = self.client.post(reverse("login_user"), {
            "email": "agent2@example.com",
            "password": "testpassword"
        })
        token2 = login2.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")

        self.client.post(self.list_url, {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "phone": "555-2222",
            "source": self.source.id
        }, format="json")

        # Login back as agent1
        login1 = self.client.post(reverse("login_user"), {
            "email": "agent1@example.com",
            "password": "testpassword"
        })
        token1 = login1.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")

        res = self.client.get(self.list_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # agent1 should only see 1 contact

    def test_retrieve_contact(self):
        """Agent can retrieve their own contact"""
        res = self.client.post(self.list_url, self.payload, format="json")
        cid = res.data["id"]

        url = reverse("contact-detail", args=[cid])
        res2 = self.client.get(url)

        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data["id"], cid)

    def test_agent_cannot_retrieve_someone_elses_contact(self):
        """Agent must NOT see another agent's contacts"""
        res1 = self.client.post(self.list_url, self.payload, format="json")
        cid = res1.data["id"]

        # Create agent2
        user2 = User.objects.create_user(
            username="agent2@example.com",
            email="agent2@example.com",
            password="testpassword"
        )

        # Login as agent2
        login2 = self.client.post(reverse("login_user"), {
            "email": "agent2@example.com",
            "password": "testpassword"
        })
        token2 = login2.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")

        # Try to retrieve agent1's contact
        url = reverse("contact-detail", args=[cid])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_contact(self):
        """Agent can update their own contact"""
        res1 = self.client.post(self.list_url, self.payload, format="json")
        cid = res1.data["id"]

        url = reverse("contact-detail", args=[cid])
        res2 = self.client.patch(url, {"phone": "999-9999"}, format="json")

        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data["phone"], "999-9999")

    def test_delete_contact(self):
        """Agent can delete their own contact"""
        res1 = self.client.post(self.list_url, self.payload, format="json")
        cid = res1.data["id"]

        url = reverse("contact-detail", args=[cid])
        res2 = self.client.delete(url)

        self.assertEqual(res2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Contact.objects.count(), 0)
