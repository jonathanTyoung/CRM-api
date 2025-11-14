from django.db import models
from .agent_profiles import AgentProfile
from .leads import Lead

class Order(models.Model):
    agent = models.ForeignKey(AgentProfile, on_delete=models.CASCADE, related_name='orders')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending','Pending'),('paid','Paid'),('fulfilled','Fulfilled')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
