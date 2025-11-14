from typing import ClassVar
from django.db import models
from django.contrib.auth.models import User

class AgentProfile(models.Model):
    objects: ClassVar[models.Manager]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="agent_profile"
    )

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    agency_name = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    profile_photo_url = models.URLField(blank=True, null=True)
    office_location = models.CharField(max_length=100, blank=True, null=True)

    # Optional but recommended metadata
    role = models.CharField(
        max_length=20,
        default="agent",   # could also be "admin"
        choices=[
            ("agent", "Agent"),
            ("admin", "Administrator"),
            ("team_lead", "Team Lead"),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.agency_name})"
