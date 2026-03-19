from rest_framework import serializers
from api.models import Opportunity, OpportunityContact


class ParticipantReadSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityContact
        fields = ["id", "contact", "role"]

    def get_contact(self, obj):
        return {
            "id": obj.contact.id,
            "first_name": obj.contact.first_name,
            "last_name": obj.contact.last_name,
            "email": obj.contact.email,
        }


class OpportunityReadSerializer(serializers.ModelSerializer):
    participants = ParticipantReadSerializer(many=True, read_only=True)

    class Meta:
        model = Opportunity
        fields = "__all__"
