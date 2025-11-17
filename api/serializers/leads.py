from rest_framework import serializers
from api.models import Lead, Contact, Source, LeadGroup
from django.contrib.auth.models import User


# ---------------------------
# READ SERIALIZER
# ---------------------------

class LeadSerializer(serializers.ModelSerializer):
    """Returned when reading leads."""

    contact_name = serializers.CharField(
        source="contact.first_name",
        read_only=True
    )

    assigned_agent_name = serializers.CharField(
        source="assigned_agent.get_full_name",
        read_only=True
    )

    source_name = serializers.CharField(
        source="source.name",
        read_only=True
    )

    class Meta:
        model = Lead
        fields = [
            "id",
            "contact",
            "contact_name",
            "assigned_agent",
            "assigned_agent_name",
            "group",
            "type",
            "status",
            "notes",
            "source",
            "source_name",
            "created_at",
            "updated_at",
        ]


# ---------------------------
# WRITE SERIALIZER
# ---------------------------

class LeadCreateUpdateSerializer(serializers.ModelSerializer):
    """Used for creating or updating leads."""

    contact_id = serializers.IntegerField()
    source_id = serializers.IntegerField(required=False, allow_null=True)
    group_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Lead
        fields = [
            "contact_id",
            "type",
            "status",
            "notes",
            "source_id",
            "group_id",
        ]

    def validate_contact_id(self, value):
        """Ensure contact exists."""
        if not Contact.objects.filter(id=value).exists():
            raise serializers.ValidationError("Contact not found.")
        return value

    def create(self, validated_data):
        contact = Contact.objects.get(id=validated_data.pop("contact_id"))
        source_id = validated_data.pop("source_id", None)
        group_id = validated_data.pop("group_id", None)

        assigned_agent = validated_data.pop("assigned_agent")  # injected in ViewSet

        lead = Lead.objects.create(
            contact=contact,
            assigned_agent=assigned_agent,
            source=Source.objects.get(id=source_id) if source_id else None,
            group=LeadGroup.objects.get(id=group_id) if group_id else None,
            **validated_data
        )

        return lead

    def update(self, instance, validated_data):
        # Update basic fields
        for field, value in validated_data.items():
            if field in ["source_id", "group_id", "contact_id"]:
                continue  # handled separately
            setattr(instance, field, value)

        # Update source
        if "source_id" in validated_data:
            sid = validated_data["source_id"]
            instance.source = Source.objects.get(id=sid) if sid else None

        # Update group
        if "group_id" in validated_data:
            gid = validated_data["group_id"]
            instance.group = LeadGroup.objects.get(id=gid) if gid else None

        instance.save()
        return instance
