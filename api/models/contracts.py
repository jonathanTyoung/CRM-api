from django.db import models
from .leads import Lead

class Contract(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='contracts')
    document_url = models.URLField()
    status = models.CharField(max_length=20, choices=[('draft','Draft'),('sent','Sent'),('signed','Signed')], default='draft')
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
