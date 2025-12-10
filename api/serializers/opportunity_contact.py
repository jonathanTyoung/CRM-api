from rest_framework import serializers
from api.models import OpportunityContact


class OpportunityContactSerializer(serializers.ModelSerializer):
    # Always read contact ID only (no nested Contact)
    contact = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OpportunityContact
        fields = ["id", "contact", "role"]
        read_only_fields = ["id", "contact"]
