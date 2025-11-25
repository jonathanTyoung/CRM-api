from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from api.models import AgentProfile
from api.serializers.agent_profiles import AgentProfileSerializer


class AgentProfileViewSet(ModelViewSet):
    """CRUD for Agent Profiles."""
    
    serializer_class = AgentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Admins can see all profiles
        if user.is_staff or user.is_superuser:
            return AgentProfile.objects.all()

        # Regular agents can see only their own profile
        return AgentProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        """
        Ensure the agent profile is always tied to the logged-in user.
        You NEVER want the frontend to manually set user_id.
        """
        serializer.save(user=self.request.user)
