from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import AgentProfile


class UserSerializer(serializers.ModelSerializer):
    """Minimal nested user serializer for agent profile."""

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")


class AgentProfileSerializer(serializers.ModelSerializer):
    """Serializer for Agent Profiles."""
    
    user = UserSerializer(read_only=True)

    class Meta:
        model = AgentProfile
        fields = (
            "id",
            "user",
            "phone_number",
            "agency_name",
            "license_number",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")
