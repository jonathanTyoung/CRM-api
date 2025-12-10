from django.db import models
from django.contrib.auth.models import User
from api.models.agent_profiles import AgentProfile
from api.models.leads import Lead


class Opportunity(models.Model):
    owner = models.ForeignKey(
        AgentProfile,
        on_delete=models.CASCADE,
        related_name="opportunities"
    )

    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )

    title = models.CharField(max_length=255)

    deal_type = models.CharField(
        max_length=20,
        choices=[("buyer", "Buyer"), ("seller", "Seller"), ("investor", "Investor")],
        default="buyer",
    )

    property_address = models.CharField(max_length=255, blank=True)
    mls_id = models.CharField(max_length=50, null=True, blank=True)

    stage = models.CharField(
        max_length=20,
        choices=[
            ("prospecting", "Prospecting"),
            ("showing", "Showing"),
            ("offer", "Offer Made"),
            ("contract", "Under Contract"),
            ("closing", "Closing Scheduled"),
            ("closed", "Closed"),
        ],
        default="prospecting",
    )

    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimated_close_date = models.DateField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    assigned_agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_opportunities",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
