from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.models import Lead
from api.serializers.leads import LeadSerializer, LeadCreateUpdateSerializer


class LeadViewSet(ModelViewSet):
    """CRUD operations for Leads with agent-based scoping."""

    permission_classes = [IsAuthenticated]

    # ---------------------------------
    # QUERYSET SCOPING
    # ---------------------------------
    def get_queryset(self):
        user = self.request.user

        qs = Lead.objects.select_related(
            "assigned_agent", "contact", "source", "group"
        ).order_by("-created_at")

        # Admins/superusers can see all leads
        if user.is_staff or user.is_superuser:
            return qs

        # Agents only see their assigned leads
        return qs.filter(assigned_agent=user.agent_profile)

    # ---------------------------------
    # SERIALIZER PICKER
    # ---------------------------------
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return LeadCreateUpdateSerializer
        return LeadSerializer

    # ---------------------------------
    # CREATE
    # ---------------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lead = serializer.save()  # assigned_agent handled in serializer

        return Response(
            LeadSerializer(lead).data,
            status=status.HTTP_201_CREATED
        )

    # ---------------------------------
    # UPDATE / PATCH
    # ---------------------------------
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)

        lead = serializer.save()

        return Response(
            LeadSerializer(lead).data,
            status=status.HTTP_200_OK
        )
