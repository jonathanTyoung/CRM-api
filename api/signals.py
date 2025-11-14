from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from api.models import AgentProfile


@receiver(post_save, sender=User)
def create_agent_profile(sender, instance, created, **kwargs):
    """
    Automatically create an AgentProfile whenever a new User is created.
    """
    if created:
        AgentProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_agent_profile(sender, instance, **kwargs):
    """
    Ensure the linked AgentProfile is saved whenever the User updates.
    """
    if hasattr(instance, "agent_profile"):
        instance.agent_profile.save()
