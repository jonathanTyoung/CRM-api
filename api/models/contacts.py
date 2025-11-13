from django.db import models
from .agent_profiles import AgentProfile


class Contact(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    owner = models.ForeignKey(AgentProfile, on_delete=models.CASCADE, related_name="contacts")
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, through='ContactTag')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
