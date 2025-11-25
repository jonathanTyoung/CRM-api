from django.db import models
from .agent_profiles import AgentProfile

class TransferRequest(models.Model):
    ENTITY_CHOICES = [
        ('lead', 'Lead'),
        ('contact', 'Contact'),
        ('lead_group', 'Lead Group'),
    ]

    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES)
    entity_id = models.PositiveIntegerField()

    from_agent = models.ForeignKey(AgentProfile, on_delete=models.CASCADE, related_name='sent_transfers')
    to_agent = models.ForeignKey(AgentProfile, on_delete=models.CASCADE, related_name='received_transfers')

    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    ], default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)