from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from api.serializers import OpportunitySerializer
from api.models import Opportunity


class StandardPagination(PageNumberPagination):
    """
    Recommended paginator:
    - Default: 20 items per page
    - Allows frontend to request custom page size: ?page_size=50
    """
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
            .select_related("contact", "lead", "assigned_agent")
            .order_by("-created_at")     # Recommended: newest first
        )

        # Admins see everything
        if user.role == "admin":
            return qs

        # Agents see only their opportunities
        return qs.filter(assigned_agent=user)

    def perform_create(self, serializer):
        """
        Recommended behavior:
        - Automatically assigns opportunity to the logged-in agent
        - Allows admin to override assigned_agent in the serializer if needed
        """
        serializer.save(assigned_agent=self.request.user)
