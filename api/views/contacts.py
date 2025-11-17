from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

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

        if user.is_staff or user.is_superuser:
            return Contact.objects.all()

        return Contact.objects.filter(owner=user.agent_profile)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ContactCreateUpdateSerializer
        return ContactSerializer

    # ---------------------------
    # CREATE
    # ---------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"owner": request.user.agent_profile}   # <-- FIXED
        )
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        read_serializer = ContactSerializer(serializer.instance)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()   # <-- DO NOT PASS owner HERE ANYMORE

    # ---------------------------
    # UPDATE
    # ---------------------------
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={"owner": request.user.agent_profile}  # <-- SAFE & CONSISTENT
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(ContactSerializer(instance).data)
