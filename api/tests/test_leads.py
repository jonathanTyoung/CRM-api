from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import Lead, Contact, Source


class LeadTests(APITestCase):
    """Tests for Lead CRUD and ownership rules."""

    def setUp(self):

        # ----------------------------
        # Agent 1 (AgentProfile auto-created by signal)
        # ----------------------------
        self.user = User.objects.create_user(
            username="agent1@example.com",
            email="agent1@example.com",
            password="testpassword"
        )
        agent1_profile = self.user.agent_profile   # auto-created

        # Login agent1
        login_res = self.client.post(reverse("login_user"), {
            "email": "agent1@example.com",
            "password": "testpassword"
        })
        token = login_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.list_url = reverse("lead-list")

        # ----------------------------
        # Related models
        # ----------------------------
        self.source = Source.objects.create(name="Referral")

        self.contact = Contact.objects.create(
            first_name="Carl",
            last_name="Buyer",
            email="carl@example.com",
            phone="111-2222",
            owner=agent1_profile,     # correct new ownership
            source=self.source
        )

        self.payload = {
            "first_name": "Carl",
            "last_name": "Buyer",
            "contact": self.contact.id,
            "type": "buying",
            "status": "new",
            "notes": "Test lead",
            "source": self.source.id
        }

    # ------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------
    def test_create_lead(self):
        """Agent can create a lead."""
        res = self.client.post(self.list_url, self.payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        lead = Lead.objects.get(id=res.data["id"])
        self.assertEqual(lead.assigned_agent, self.user.agent_profile)

    # ------------------------------------------------------------
    # LIST
    # ------------------------------------------------------------
    def test_list_leads(self):
        """Agent only sees their own leads."""
        self.client.post(self.list_url, self.payload, format="json")

        res = self.client.get(self.list_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    # ------------------------------------------------------------
    # RETRIEVE
    # ------------------------------------------------------------
    def test_retrieve_lead(self):
        """Agent can retrieve their own lead."""
        res = self.client.post(self.list_url, self.payload, format="json")
        lid = res.data["id"]

        url = reverse("lead-detail", args=[lid])
        res2 = self.client.get(url)

        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data["id"], lid)

    # ------------------------------------------------------------
    # PERMISSION CHECK
    # ------------------------------------------------------------
    def test_agent_cannot_see_other_agents_leads(self):
        """Leads must NOT be visible across agents."""
        res = self.client.post(self.list_url, self.payload, format="json")
        lid = res.data["id"]

        # ----------------------------
        # Agent 2
        # ----------------------------
        user2 = User.objects.create_user(
            username="agent2@example.com",
            email="agent2@example.com",
            password="testpassword"
        )
        user2_profile = user2.agent_profile  # auto-created

        # Login agent2
        login2 = self.client.post(reverse("login_user"), {
            "email": "agent2@example.com",
            "password": "testpassword"
        })
        token2 = login2.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")

        # agent2 should NOT see agent1's lead
        url = reverse("lead-detail", args=[lid])
        res2 = self.client.get(url)

        self.assertEqual(res2.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------
    def test_update_lead(self):
        """Agent can update their own lead."""
        res = self.client.post(self.list_url, self.payload, format="json")
        lid = res.data["id"]

        url = reverse("lead-detail", args=[lid])
        res2 = self.client.patch(url, {"status": "contacted"}, format="json")

        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data["status"], "contacted")

    # ------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------
    def test_delete_lead(self):
        """Agent can delete their own lead."""
        res = self.client.post(self.list_url, self.payload, format="json")
        lid = res.data["id"]

        url = reverse("lead-detail", args=[lid])
        delete_res = self.client.delete(url)

        self.assertEqual(delete_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lead.objects.count(), 0)
