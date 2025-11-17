from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.models import Lead
from api.serializers.leads import (
    LeadSerializer,
    LeadCreateUpdateSerializer
)


class LeadViewSet(ModelViewSet):
    """CRUD operations for Leads with agent scoping."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Admins get all leads
        if user.is_staff or user.is_superuser:
            return Lead.objects.all().order_by("-created_at")

        # Agents only see leads assigned to them
        return Lead.objects.filter(
            assigned_agent=user
        ).order_by("-created_at")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return LeadCreateUpdateSerializer
        return LeadSerializer

    def perform_create(self, serializer):
        """
        Automatically assign lead to logged-in agent.
        """
        serializer.save(assigned_agent=self.request.user)

    def perform_update(self, serializer):
        """
        Optional: ensure only assigned agents can update.
        """
        instance = self.get_object()

        # If you want:
        # if instance.assigned_agent != self.request.user:
        #     raise PermissionDenied("You cannot modify this lead.")

        serializer.save()
