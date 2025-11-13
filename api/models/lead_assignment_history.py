from django.db import models
from .leads import Lead
from .agent_profiles import AgentProfile

class LeadAssignmentHistory(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='assignment_history')
    previous_agent = models.ForeignKey(AgentProfile, on_delete=models.SET_NULL, null=True, related_name='previous_assignments')
    new_agent = models.ForeignKey(AgentProfile, on_delete=models.SET_NULL, null=True, related_name='new_assignments')
    changed_by = models.ForeignKey(AgentProfile, on_delete=models.SET_NULL, null=True, related_name='assignments_changed')
    changed_at = models.DateTimeField(auto_now_add=True)