from django.db.models import Q
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
    """CRUD operations for contacts with owner scoping and search."""

    permission_classes = [IsAuthenticated]

    # ---------------------------
    # QUERYSET (scoping + search)
    # ---------------------------
    def get_queryset(self):
        user = self.request.user

        # Admins see everything, agents see only their own contacts
        if user.is_staff or user.is_superuser:
            qs = Contact.objects.all()
        else:
            qs = Contact.objects.filter(owner=user.agent_profile)

        # Optional search filtering
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )

        # Stable descending order (latest first)
        return qs.order_by("-id")

    # ---------------------------
    # READ vs WRITE Serializers
    # ---------------------------
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ContactCreateUpdateSerializer
        return ContactSerializer

    # ---------------------------
    # EXTRA CONTEXT FOR WRITES
    # ---------------------------
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["owner"] = self.request.user.agent_profile
        return context

    # ---------------------------
    # CREATE
    # ---------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()

        return Response(
            ContactSerializer(contact).data,
            status=status.HTTP_201_CREATED,
        )

    # ---------------------------
    # UPDATE
    # ---------------------------
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        return Response(ContactSerializer(updated).data)
