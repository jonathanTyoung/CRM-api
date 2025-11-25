from django.db import models
from .agent_profiles import AgentProfile
from .sources import Source
from .tags import Tag


class Contact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('prospect', 'Prospect'),        # default when converted from Lead
        ('client', 'Client'),            # buyer/seller who closed a deal
        ('past_client', 'Past Client'),
        ('referral', 'Referral Source'),
        ('vendor', 'Vendor / Business Contact'),
        ('sphere', 'Sphere of Influence'),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

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
        return f"{self.first_name} {self.last_name}"
