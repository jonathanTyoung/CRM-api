from django.db import models
from .agent_profiles import AgentProfile
from .sources import Source
from .tags import Tag


class Contact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('prospect', 'Prospect'),
        ('client', 'Client'),
        ('past_client', 'Past Client'),
        ('referral', 'Referral Source'),
        ('vendor', 'Vendor / Business Contact'),
        ('sphere', 'Sphere of Influence'),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    owner = models.ForeignKey(
        AgentProfile,
        on_delete=models.CASCADE,
        related_name="contacts"
    )

    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        default='prospect'
    )

    source = models.ForeignKey(
        Source,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    tags = models.ManyToManyField(Tag, through='ContactTag')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        last = f" {self.last_name}" if self.last_name else ""
        return f"{self.first_name}{last}"
