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

    # ---------------------------
    # QUERYSET SCOPING
    # ---------------------------


    def get_queryset(self):
        print("🔶 DJANGO RECEIVED AUTH:", self.request.headers.get("Authorization"))
        user = self.request.user

        if user.is_staff or user.is_superuser:
            qs = Contact.objects.all()
        else:
            qs = Contact.objects.filter(owner=user.agent_profile)

        return qs.order_by("-id")  # consistent pagination order

    # ---------------------------
    # READ vs WRITE Serializers
    # ---------------------------
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ContactCreateUpdateSerializer
        return ContactSerializer

    # ---------------------------
    # ONE PLACE TO ADD CONTEXT
    # ---------------------------
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["owner"] = self.request.user.agent_profile
        return context

    # ---------------------------
    # CREATE (Use DRF default, but return read format)
    # ---------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        read_serializer = ContactSerializer(instance)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    # ---------------------------
    # UPDATE (PATCH or PUT)
    # ---------------------------
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response(ContactSerializer(instance).data)
