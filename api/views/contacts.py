from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.models import Contact
from api.serializers.contacts import (
    ContactSerializer,
    ContactCreateUpdateSerializer,
)


class ContactViewSet(ModelViewSet):
    """CRUD operations for contacts with owner scoping."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Admins see everything
        if user.is_staff or user.is_superuser:
            return Contact.objects.all()

        # Agents only see their own contacts
        return Contact.objects.filter(owner=user.agent_profile)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ContactCreateUpdateSerializer
        return ContactSerializer

    def perform_create(self, serializer):
        """
        Automatically attach the contact to
        the currently logged-in agent.
        """
        serializer.save(owner=self.request.user.agent_profile)

    def perform_update(self, serializer):
        """
        Optional: enforce ownership (just good practice)
        """
        instance = self.get_object()
        if instance.owner != self.request.user.agent_profile:
            # If you want: raise PermissionDenied
            pass

        serializer.save()
