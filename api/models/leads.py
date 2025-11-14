from django.db import models
from django.contrib.auth.models import User
from .contacts import Contact
from .sources import Source
from .lead_groups import LeadGroup

class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('pending_offer', 'Pending Offer'),
        ('closed', 'Closed'),
    ]

    TYPE_CHOICES = [
        ('buying', 'Buying'),
        ('selling', 'Selling'),
    ]

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='leads')

    # Assigned agent should reference User (identity)
    assigned_agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_leads')

    # Optional grouping feature
    group = models.ForeignKey(
        LeadGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True)
    notes = models.TextField(blank=True)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 🟢 FIXED indentation on update_status()
    def update_status(self, new_status):
        self.status = new_status
        self.save()

    def __str__(self):
        return f"Lead: {self.contact.first_name} {self.contact.last_name}"

    class Meta:
        ordering = ['-created_at']   # 🟢 NEW: default ordering (newest first)
