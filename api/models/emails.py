from django.db import models
from .agents import Agent
from .leads import Lead

class EmailTemplate(models.Model):
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=500)
    body = models.TextField()
    created_by = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmailSent(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='emails_sent')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=500)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('sent','Sent'),('failed','Failed')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
