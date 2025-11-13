from django.db import models
from .agent_profiles import AgentProfile
from .leads import Lead
from .listings import Listing

class AddOn(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Order(models.Model):
    agent = models.ForeignKey(AgentProfile, on_delete=models.CASCADE, related_name='orders')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending','Pending'),('paid','Paid'),('fulfilled','Fulfilled')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    add_on = models.ForeignKey(AddOn, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[('pending','Pending'),('completed','Completed'),('refunded','Refunded')], default='pending')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
