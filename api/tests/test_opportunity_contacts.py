from django.test import TestCase
from django.contrib.auth.models import User
from api.models import Contact, Opportunity, OpportunityContact, AgentProfile
from rest_framework.test import APIClient


class OpportunityContactTests(TestCase):
    def setUp(self):
        # Create agent/user
        self.user = User.objects.create_user(username="agent", password="pass123")
        self.agent_profile, _ = AgentProfile.objects.get_or_create(
            user=self.user, defaults={"role": "agent"}
        )

        # Contacts owned by agent
        self.contact1 = Contact.objects.create(
            first_name="John", last_name="Doe", owner=self.agent_profile
        )
        self.contact2 = Contact.objects.create(
            first_name="Jane", last_name="Doe", owner=self.agent_profile
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # --------------------------------------------------------
    # CREATE MULTIPLE PARTICIPANTS
    # --------------------------------------------------------
    def test_create_opportunity_with_multiple_contacts(self):
        payload = {
            "title": "123 Main St Opportunity",
            "participants": [
                {"contact": self.contact1.id, "role": "Buyer"},
                {"contact": self.contact2.id, "role": "Co-buyer"},
            ],
        }

        response = self.client.post("/api/opportunities/", payload, format="json")
        self.assertEqual(response.status_code, 201)

        opp = Opportunity.objects.first()
        links = OpportunityContact.objects.filter(opportunity=opp)
        self.assertEqual(links.count(), 2)

    # --------------------------------------------------------
    # DUPLICATE PARTICIPANTS SHOULD NOT BE ALLOWED
    # --------------------------------------------------------
    def test_prevent_duplicate_participants(self):
        opp = Opportunity.objects.create(
            title="Test Deal",
            owner=self.agent_profile,
            assigned_agent=self.agent_profile,
        )

        # First link OK
        OpportunityContact.objects.create(opportunity=opp, contact=self.contact1)

        # Duplicate link should raise IntegrityError (unique_together)
        with self.assertRaises(Exception):
            OpportunityContact.objects.create(opportunity=opp, contact=self.contact1)

    # --------------------------------------------------------
    # PATCH UPDATES SHOULD REPLACE PARTICIPANT LIST
    # --------------------------------------------------------
    def test_serializer_replaces_participants_on_update(self):
        # CREATE OPPORTUNITY
        create_payload = {
            "title": "Test Multi",
            "participants": [{"contact": self.contact1.id, "role": "Buyer"}],
        }

        response = self.client.post("/api/opportunities/", create_payload, format="json")
        self.assertEqual(response.status_code, 201)

        opp_id = response.data["id"]

        # UPDATE — replace with contact2 only
        update_payload = {
            "participants": [{"contact": self.contact2.id, "role": "Investor"}]
        }

        response = self.client.patch(
            f"/api/opportunities/{opp_id}/", update_payload, format="json"
        )
        self.assertEqual(response.status_code, 200)

        # Validate DB state
        links = OpportunityContact.objects.filter(opportunity_id=opp_id)
        self.assertEqual(links.count(), 1)
        self.assertEqual(links.first().contact, self.contact2)
