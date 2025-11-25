from django.contrib.auth.models import User
from django.db import models
from .contacts import Contact
from .leads import Lead

class Opportunity(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="opportunities")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="opportunities")
    assigned_agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="opportunities")

    title = models.CharField(max_length=255)
    deal_type = models.CharField(
        max_length=20,
        choices=[('buyer', 'Buyer'), ('seller', 'Seller'), ('investor', 'Investor')],
        default='buyer'
    )

    property_address = models.CharField(max_length=255, blank=True)
    mls_id = models.CharField(max_length=50, blank=True, null=True)

    stage = models.CharField(
        max_length=20,
        choices=[
            ('prospecting', 'Prospecting'),
            ('showing', 'Showing'),
            ('offer', 'Offer Made'),
            ('contract', 'Under Contract'),
            ('closing', 'Closing Scheduled'),
            ('closed', 'Closed'),
        ],
        default='prospecting'
    )

    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimated_close_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
