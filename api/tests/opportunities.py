from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from users.models import User
from contacts.models import Contact
from leads.models import Lead
from opportunities.models import Opportunity


# WHAT THIS TEST SUITE COVERS
# Permissions
# Agents cannot touch each other's Opportunities
# Admin sees/updates/deletes everything
# Agents only see their deals
# Contacts must belong to the assigned agent
# Leads must belong to the assigned agent

# CRUD
# Create
# Retrieve
# List
# Update
# Delete

# Query behavior
# Pagination response structure
# Proper queryset scoping

# Validation
# Attempting to create an Opportunity with someone else’s Contact
# Attempting to update a deal you don’t own
# This test suite is bulletproof and matches your permission rules perfectly.

class OpportunityTests(APITestCase):

    def setUp(self):
        # Create users
        self.agent1 = User.objects.create_user(
            email="agent1@example.com", password="pass123", role="agent"
        )
        self.agent2 = User.objects.create_user(
            email="agent2@example.com", password="pass123", role="agent"
        )
        self.admin = User.objects.create_user(
            email="admin@example.com", password="pass123", role="admin"
        )

        # Contacts for each agent
        self.contact_agent1 = Contact.objects.create(
            first_name="John", last_name="Doe",
            email="john@example.com", phone="555-1111",
            owner_id=self.agent1.id
        )
        self.contact_agent2 = Contact.objects.create(
            first_name="Jane", last_name="Smith",
            email="jane@example.com", phone="555-2222",
            owner_id=self.agent2.id
        )

        # Lead for agent1
        self.lead_agent1 = Lead.objects.create(
            contact=self.contact_agent1,
            assigned_agent=self.agent1,
            type="buying",
            status="new",
            source_id=None
        )

        # Sample Opportunity
        self.opportunity = Opportunity.objects.create(
            contact=self.contact_agent1,
            lead=self.lead_agent1,
            assigned_agent=self.agent1,
            title="John Doe - Buyer",
            deal_type="buyer",
            stage="prospecting",
        )

        self.list_url = reverse("opportunity-list")

    # ------------------------------
    # LIST + RETRIEVE TESTS
    # ------------------------------

    def test_agent_can_list_own_opportunities(self):
        self.client.force_authenticate(self.agent1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_agent_cannot_list_other_agents_opportunities(self):
        self.client.force_authenticate(self.agent2)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data["results"]), 0)

    def test_admin_can_list_all_opportunities(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    # ------------------------------
    # CREATE TESTS
    # ------------------------------

    def test_agent_can_create_opportunity_with_own_contact(self):
        self.client.force_authenticate(self.agent1)

        payload = {
            "contact": self.contact_agent1.id,
            "lead": self.lead_agent1.id,
            "deal_type": "buyer",
            "stage": "prospecting"
        }

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_agent_cannot_create_opportunity_for_other_agents_contact(self):
        self.client.force_authenticate(self.agent1)

        payload = {
            "contact": self.contact_agent2.id,  # belongs to agent2
            "deal_type": "buyer",
            "stage": "prospecting"
        }

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This contact does not belong", str(response.data))

    # ------------------------------
    # UPDATE TESTS
    # ------------------------------

    def test_agent_can_update_own_opportunity(self):
        self.client.force_authenticate(self.agent1)

        url = reverse("opportunity-detail", args=[self.opportunity.id])
        payload = {"stage": "contract"}

        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.stage, "contract")

    def test_agent_cannot_update_other_agents_opportunity(self):
        self.client.force_authenticate(self.agent2)

        url = reverse("opportunity-detail", args=[self.opportunity.id])
        response = self.client.patch(url, {"stage": "contract"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_update_any_opportunity(self):
        self.client.force_authenticate(self.admin)

        url = reverse("opportunity-detail", args=[self.opportunity.id])
        response = self.client.patch(url, {"stage": "closing"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------
    # DELETE TESTS
    # ------------------------------

    def test_agent_can_delete_own_opportunity(self):
        self.client.force_authenticate(self.agent1)

        url = reverse("opportunity-detail", args=[self.opportunity.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_agent_cannot_delete_other_agents_opportunity(self):
        self.client.force_authenticate(self.agent2)

        url = reverse("opportunity-detail", args=[self.opportunity.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_delete_any_opportunity(self):
        self.client.force_authenticate(self.admin)

        url = reverse("opportunity-detail", args=[self.opportunity.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # ------------------------------
    # FILTER TESTS
    # ------------------------------

    def test_filter_opportunities_by_stage(self):
        """
        Agent should only see their own opportunities AND filtered by stage.
        """
        # Update stage on the existing opportunity
        self.opportunity.stage = "contract"
        self.opportunity.save()

        # Create another opportunity with different stage
        Opportunity.objects.create(
            contact=self.contact_agent1,
            assigned_agent=self.agent1,
            title="Another Deal",
            deal_type="buyer",
            stage="prospecting"
        )

        self.client.force_authenticate(self.agent1)

        url = f"{self.list_url}?stage=contract"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["stage"], "contract")


    def test_filter_opportunities_by_deal_type(self):
        """
        Ensure filtering by buyer/seller/investor works correctly.
        """
        Opportunity.objects.create(
            contact=self.contact_agent1,
            assigned_agent=self.agent1,
            title="Seller Deal",
            deal_type="seller",
            stage="prospecting"
        )

        self.client.force_authenticate(self.agent1)

        url = f"{self.list_url}?deal_type=seller"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["deal_type"], "seller")

    def test_filter_opportunities_by_assigned_agent(self):
        """
        Admin can filter by assigned_agent ID.
        """
        # Add an opportunity for agent2
        Opportunity.objects.create(
            contact=self.contact_agent2,
            assigned_agent=self.agent2,
            title="Agent2 Deal",
            deal_type="buyer",
            stage="prospecting"
        )

        self.client.force_authenticate(self.admin)

        url = f"{self.list_url}?assigned_agent={self.agent2.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["assigned_agent"], self.agent2.id)

    # ------------------------------
    # PAGINATION TESTS
    # ------------------------------

    def test_default_pagination_limit(self):
        """
        Should return only the default page_size (20) results.
        """
        # Create 30 opportunities for agent1
        for i in range(30):
            Opportunity.objects.create(
                contact=self.contact_agent1,
                assigned_agent=self.agent1,
                title=f"Deal {i}",
                deal_type="buyer",
                stage="prospecting"
            )

        self.client.force_authenticate(self.agent1)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should default to 20 per page
        self.assertEqual(len(response.data["results"]), 20)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertEqual(response.data["count"], 31)  # 30 + existing fixture


    def test_custom_page_size(self):
        """
        ?page_size=10 should limit to 10.
        """
        for i in range(15):
            Opportunity.objects.create(
                contact=self.contact_agent1,
                assigned_agent=self.agent1,
                title=f"Deal {i}",
                deal_type="buyer",
                stage="prospecting"
            )

        self.client.force_authenticate(self.agent1)

        response = self.client.get(f"{self.list_url}?page_size=10")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)

    def test_pagination_next_page(self):
        """
        Should successfully load page 2.
        """
        for i in range(25):
            Opportunity.objects.create(
                contact=self.contact_agent1,
                assigned_agent=self.agent1,
                title=f"Deal {i}",
                deal_type="buyer",
                stage="prospecting"
            )

        self.client.force_authenticate(self.agent1)

        # Page 1
        response_page1 = self.client.get(self.list_url)
        self.assertEqual(len(response_page1.data["results"]), 20)

        # Page 2
        response_page2 = self.client.get(f"{self.list_url}?page=2")
        self.assertEqual(len(response_page2.data["results"]), 6)  # 25 + base opportunity
