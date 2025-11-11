from django.db import models
from django.contrib.auth.models import User

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="agent_profile")
    phone_number = models.CharField(max_length=20, blank=True)
    agency_name = models.CharField(max_length=100, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    # add any other custom fields

    def __str__(self):
        return f"{self.user.username} - {self.agency_name}"
