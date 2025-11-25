from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Opportunity, Contact, Lead



class OpportunitySerializer(serializers.ModelSerializer):
    contact = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all())
    lead = serializers.PrimaryKeyRelatedField(
        queryset=Lead.objects.all(),
        allow_null=True,
        required=False
    )
    assigned_agent = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "contact",
            "lead",
            "assigned_agent",
            "title",
            "deal_type",
            "property_address",
            "mls_id",
            "stage",
            "price",
            "estimated_close_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        """Validates agent-contact-lead relationships for security."""
        request_user = self.context["request"].user
        contact = attrs.get("contact")
        lead = attrs.get("lead")
        agent = attrs.get("assigned_agent") or request_user

        # Contact must belong to assigned agent
        if contact.owner_id != agent.id:
            raise serializers.ValidationError(
                "This contact does not belong to the assigned agent."
            )

        # If a lead is provided, it must belong to the same agent
        if lead and lead.assigned_agent_id != agent.id:
            raise serializers.ValidationError(
                "This lead is not assigned to the selected agent."
            )

        return attrs

    def create(self, validated_data):
        """Auto-assign agent and auto-generate title."""
        request_user = self.context["request"].user

        # Default to request user if admin didn't manually assign
        if "assigned_agent" not in validated_data:
            validated_data["assigned_agent"] = request_user

        # Auto-generate title if none provided
        if not validated_data.get("title"):
            contact = validated_data["contact"]
            deal_type = validated_data.get("deal_type", "buyer").capitalize()
            validated_data["title"] = (
                f"{contact.first_name} {contact.last_name} - {deal_type} Opportunity"
            )

        return super().create(validated_data)
