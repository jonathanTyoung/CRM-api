from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from api.models import AgentProfile

@receiver(post_save, sender=User)
def create_agent_profile(sender, instance, created, **kwargs):
    """
    Automatically create an AgentProfile when a User is created.
    Guaranteed to run only once per user.
    """
    if created:
        AgentProfile.objects.create(user=instance, role="agent")
