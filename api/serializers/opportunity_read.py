from rest_framework import serializers
from api.models import Opportunity
from api.serializers.opportunity_contact import OpportunityContactSerializer

class OpportunityReadSerializer(serializers.ModelSerializer):
    participants = OpportunityContactSerializer(many=True, read_only=True)

    class Meta:
        model = Opportunity
        fields = "__all__"
