from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from api.models import Contact, Lead, Opportunity, AgentProfile, OpportunityContact


class OpportunityTests(APITestCase):

    def setUp(self):
        # -----------------------
        # USERS (AgentProfiles auto-created by signals)
        # -----------------------
        self.agent1 = User.objects.create_user(
            username="agent1@example.com",
            email="agent1@example.com",
            password="pass123",
            first_name="A",
            last_name="One",
        )
        self.agent1_profile = self.agent1.agent_profile
        self.agent1_profile.role = "agent"
        self.agent1_profile.save()

        self.agent2 = User.objects.create_user(
            username="agent2@example.com",
            email="agent2@example.com",
            password="pass123",
            first_name="B",
            last_name="Two",
        )
        self.agent2_profile = self.agent2.agent_profile
        self.agent2_profile.role = "agent"
        self.agent2_profile.save()

        self.admin = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="pass123",
            first_name="Admin",
            last_name="User",
        )
        self.admin_profile = self.admin.agent_profile
        self.admin_profile.role = "admin"
        self.admin_profile.save()

        # -----------------------
        # CONTACTS
        # -----------------------
        self.contact_agent1 = Contact.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="555-1111",
            owner=self.agent1_profile,
        )
        self.contact_agent2 = Contact.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="555-2222",
            owner=self.agent2_profile,
        )

        # -----------------------
        # LEAD for agent1
        # -----------------------
        self.lead_agent1 = Lead.objects.create(
            contact=self.contact_agent1,
            assigned_agent=self.agent1,
            type="buying",
            status="new",
            source=None,
        )

        # -----------------------
        # OPPORTUNITY FIXTURE
        # -----------------------
        self.opportunity = Opportunity.objects.create(
            owner=self.agent1_profile,
            assigned_agent=self.agent1,
            title="John Doe - Buyer",
            deal_type="buyer",
            stage="prospecting",
        )

        # Attach participant
        OpportunityContact.objects.create(
            opportunity=self.opportunity,
            contact=self.contact_agent1,
            role="buyer",
        )

        self.list_url = reverse("opportunity-list")

    # ----------------------------------------------------
    # LIST TESTS
    # ----------------------------------------------------
    def test_agent_can_list_own_opportunities(self):
        self.client.force_authenticate(self.agent1)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_agent_cannot_list_other_agents_opportunities(self):
        self.client.force_authenticate(self.agent2)
        res = self.client.get(self.list_url)
        self.assertEqual(len(res.data["results"]), 0)

    def test_admin_can_list_all_opportunities(self):
        self.client.force_authenticate(self.admin)
        res = self.client.get(self.list_url)
        self.assertEqual(len(res.data["results"]), 1)

    # ----------------------------------------------------
    # CREATE TESTS
    # ----------------------------------------------------
    def test_agent_can_create_opportunity_with_own_contact(self):
        self.client.force_authenticate(self.agent1)

        payload = {
            "title": "New Deal",
            "deal_type": "buyer",
            "stage": "prospecting",
            "participants": [
                {"contact": self.contact_agent1.id, "role": "buyer"}
            ],
        }

        res = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_agent_cannot_create_opportunity_for_other_agents_contact(self):
        self.client.force_authenticate(self.agent1)

        payload = {
            "title": "Bad Deal",
            "deal_type": "buyer",
            "stage": "prospecting",
            "participants": [
                {"contact": self.contact_agent2.id, "role": "buyer"}
            ],
        }

        res = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("does not belong", str(res.data))

    # ----------------------------------------------------
    # UPDATE TESTS
    # ----------------------------------------------------
    def test_agent_can_update_own_opportunity(self):
        self.client.force_authenticate(self.agent1)
        url = reverse("opportunity-detail", args=[self.opportunity.id])
        res = self.client.patch(url, {"stage": "contract"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.stage, "contract")

    def test_agent_cannot_update_other_agents_opportunity(self):
        self.client.force_authenticate(self.agent2)
        url = reverse("opportunity-detail", args=[self.opportunity.id])
        res = self.client.patch(url, {"stage": "closing"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_update_any_opportunity(self):
        self.client.force_authenticate(self.admin)
        url = reverse("opportunity-detail", args=[self.opportunity.id])
        res = self.client.patch(url, {"stage": "closing"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------
    # DELETE TESTS
    # ----------------------------------------------------
    def test_agent_can_delete_own_opportunity(self):
        self.client.force_authenticate(self.agent1)
        url = reverse("opportunity-detail", args=[self.opportunity.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_agent_cannot_delete_other_agents_opportunity(self):
        self.client.force_authenticate(self.agent2)
        url = reverse("opportunity-detail", args=[self.opportunity.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_delete_any_opportunity(self):
        self.client.force_authenticate(self.admin)
        url = reverse("opportunity-detail", args=[self.opportunity.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    # ----------------------------------------------------
    # FILTERS
    # ----------------------------------------------------
    def test_filter_opportunities_by_stage(self):
        self.opportunity.stage = "contract"
        self.opportunity.save()

        Opportunity.objects.create(
            owner=self.agent1_profile,
            assigned_agent=self.agent1,
            title="Another",
            deal_type="buyer",
            stage="prospecting",
        )

        self.client.force_authenticate(self.agent1)
        res = self.client.get(f"{self.list_url}?stage=contract")

        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["stage"], "contract")

    def test_filter_opportunities_by_deal_type(self):
        Opportunity.objects.create(
            owner=self.agent1_profile,
            assigned_agent=self.agent1,
            title="Seller Deal",
            deal_type="seller",
            stage="prospecting",
        )

        self.client.force_authenticate(self.agent1)
        res = self.client.get(f"{self.list_url}?deal_type=seller")

        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["deal_type"], "seller")

    def test_filter_opportunities_by_assigned_agent(self):
        Opportunity.objects.create(
            owner=self.agent2_profile,
            assigned_agent=self.agent2,
            title="Agent2 Deal",
            deal_type="buyer",
            stage="prospecting",
        )

        self.client.force_authenticate(self.admin)
        res = self.client.get(f"{self.list_url}?assigned_agent={self.agent2.id}")

        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["assigned_agent"], self.agent2.id)

    # ----------------------------------------------------
    # PAGINATION
    # ----------------------------------------------------
    def test_default_pagination_limit(self):
        for i in range(30):
            Opportunity.objects.create(
                owner=self.agent1_profile,
                assigned_agent=self.agent1,
                title=f"Deal {i}",
                deal_type="buyer",
                stage="prospecting",
            )

        self.client.force_authenticate(self.agent1)
        res = self.client.get(self.list_url)

        self.assertEqual(len(res.data["results"]), 20)
        self.assertEqual(res.data["count"], 31)

    def test_custom_page_size(self):
        for i in range(15):
            Opportunity.objects.create(
                owner=self.agent1_profile,
                assigned_agent=self.agent1,
                title=f"Deal {i}",
                deal_type="buyer",
                stage="prospecting",
            )

        self.client.force_authenticate(self.agent1)
        res = self.client.get(f"{self.list_url}?page_size=10")

        self.assertEqual(len(res.data["results"]), 10)

    def test_pagination_next_page(self):
        for i in range(25):
            Opportunity.objects.create(
                owner=self.agent1_profile,
                assigned_agent=self.agent1,
                title=f"Deal {i}",
                deal_type="buyer",
                stage="prospecting",
            )

        self.client.force_authenticate(self.agent1)

        res1 = self.client.get(self.list_url)
        self.assertEqual(len(res1.data["results"]), 20)

        res2 = self.client.get(f"{self.list_url}?page=2")
        self.assertEqual(len(res2.data["results"]), 6)
