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
from api.permissions import is_crm_admin


class ContactViewSet(ModelViewSet):
    """CRUD operations for contacts with strict owner scoping + search."""

    permission_classes = [IsAuthenticated]

    # ---------------------------------------
    # QUERYSET (scoping + search)
    # ---------------------------------------
    def get_queryset(self):
        user = self.request.user

        # Admins see everything; agents see only THEIR contacts
        if is_crm_admin(user):
            qs = Contact.objects.select_related("owner__user", "source").prefetch_related("tags")
        else:
            qs = Contact.objects.select_related("owner__user", "source").prefetch_related("tags").filter(owner=user.agent_profile)

        # Search parameter (simple keyword search)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )

        # Relationship type filter
        relationship_type = self.request.query_params.get("relationship_type")
        if relationship_type:
            qs = qs.filter(relationship_type=relationship_type)

        # Tag filter (by tag ID)
        tag_id = self.request.query_params.get("tag")
        if tag_id:
            qs = qs.filter(tags__id=tag_id)

        return qs.order_by("-id")

    # ---------------------------------------
    # SELECT SERIALIZER
    # ---------------------------------------
    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ContactCreateUpdateSerializer
        return ContactSerializer

    # ---------------------------------------
    # CREATE CONTACT
    # ---------------------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},  # ensures user.agent_profile is available
        )
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()

        return Response(
            ContactSerializer(contact).data,
            status=status.HTTP_201_CREATED,
        )

    # ---------------------------------------
    # UPDATE CONTACT
    # ---------------------------------------
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()

        return Response(ContactSerializer(contact).data)
