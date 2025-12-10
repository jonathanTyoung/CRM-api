from django.db import models
from .opportunities import Opportunity
from .contacts import Contact


class OpportunityContact(models.Model):
    opportunity = models.ForeignKey(
        Opportunity,
        related_name="participants",
        on_delete=models.CASCADE
    )
    contact = models.ForeignKey(
        Contact,
        related_name="opportunities",
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ("opportunity", "contact")

    def __str__(self):
        return f"{self.contact} → {self.opportunity} ({self.role})"
