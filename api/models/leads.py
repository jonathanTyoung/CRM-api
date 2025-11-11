from django.db import models
from .agents import Agent
from .contacts import Contact, Source

class LeadGroup(models.Model):
    name = models.CharField(max_length=255)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="lead_groups")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    assigned_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='leads')
    group = models.ForeignKey(LeadGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LeadAssignmentHistory(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='assignment_history')
    previous_agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, related_name='previous_assignments')
    new_agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, related_name='new_assignments')
    changed_by = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, related_name='assignments_changed')
    changed_at = models.DateTimeField(auto_now_add=True)

class TransferRequest(models.Model):
    ENTITY_CHOICES = [
        ('lead', 'Lead'),
        ('contact', 'Contact'),
        ('lead_group', 'Lead Group'),
    ]
    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES)
    entity_id = models.PositiveIntegerField()
    from_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='sent_transfers')
    to_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='received_transfers')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
