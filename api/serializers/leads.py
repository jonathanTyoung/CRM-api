from rest_framework import serializers
from api.models import Lead, Contact, Source, LeadGroup
from django.contrib.auth.models import User


# ---------------------------------
# READ SERIALIZER
# ---------------------------------

class LeadSerializer(serializers.ModelSerializer):
    """Serializer for reading leads (GET)."""

    contact_id = serializers.IntegerField(source="contact.id", read_only=True)
    assigned_agent_id = serializers.IntegerField(source="assigned_agent.id", read_only=True)
    source_id = serializers.IntegerField(source="source.id", read_only=True)
    group_id = serializers.IntegerField(source="group.id", read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id",
            "contact_id",
            "assigned_agent_id",
            "group_id",
            "type",
            "status",
            "notes",
            "source_id",
            "created_at",
            "updated_at",
        ]


# ---------------------------------
# WRITE SERIALIZER
# ---------------------------------

class LeadCreateUpdateSerializer(serializers.ModelSerializer):

    contact = serializers.IntegerField()
    source = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Lead
        fields = [
            "contact",
            "type",
            "status",
            "notes",
            "source",
        ]

    def create(self, validated_data):
        contact_id = validated_data.pop("contact")
        source_id = validated_data.pop("source", None)

        assigned_agent = self.context["request"].user

        lead = Lead.objects.create(
            contact=Contact.objects.get(id=contact_id),
            assigned_agent=assigned_agent,
            source=Source.objects.get(id=source_id) if source_id else None,
            **validated_data
        )

        return lead

    def update(self, instance, validated_data):
        if "contact" in validated_data:
            instance.contact = Contact.objects.get(id=validated_data["contact"])

        if "source" in validated_data:
            sid = validated_data["source"]
            instance.source = Source.objects.get(id=sid) if sid else None

        # Update simple fields
        for field in ["type", "status", "notes"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance

