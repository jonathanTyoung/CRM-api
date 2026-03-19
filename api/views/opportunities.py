from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from api.serializers.opportunities import OpportunitySerializer
from api.serializers.opportunity_read import OpportunityReadSerializer
from api.models import Opportunity
from api.permissions import is_crm_admin


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class OpportunityViewSet(ModelViewSet):
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["stage", "deal_type", "assigned_agent"]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Opportunity.objects
            .select_related("lead", "assigned_agent__user", "owner__user")
            .prefetch_related("participants__contact")
            .order_by("-created_at")
        )

        if not is_crm_admin(user):
            qs = qs.filter(assigned_agent=user.agent_profile)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(property_address__icontains=search)
            )

        contact_id = self.request.query_params.get("contact")
        if contact_id:
            qs = qs.filter(participants__contact_id=contact_id)

        return qs

    def perform_create(self, serializer):
        serializer.save(assigned_agent=self.request.user.agent_profile)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return OpportunitySerializer  # WRITE
        return OpportunityReadSerializer  # READ
