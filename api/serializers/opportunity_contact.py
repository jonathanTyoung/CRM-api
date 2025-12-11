from rest_framework import serializers
from api.models import OpportunityContact, Contact


class OpportunityContactSerializer(serializers.ModelSerializer):
    contact = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all()
    )

    class Meta:
        model = OpportunityContact
        fields = ["id", "contact", "role"]
        read_only_fields = ["id"]

