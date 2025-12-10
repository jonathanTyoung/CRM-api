from rest_framework import serializers
from api.models import Lead, Contact, Source, LeadGroup


# ---------------------------------
# READ SERIALIZER
# ---------------------------------

class LeadSerializer(serializers.ModelSerializer):
    contact_id = serializers.IntegerField(source="contact.id", read_only=True)
    source_id = serializers.IntegerField(source="source.id", read_only=True)
    group_id = serializers.IntegerField(source="group.id", read_only=True)
    assigned_agent_id = serializers.IntegerField(source="assigned_agent.id", read_only=True)

    # Optional but very helpful in UI
    assigned_agent_first_name = serializers.CharField(
        source="assigned_agent.first_name", read_only=True
    )
    assigned_agent_last_name = serializers.CharField(
        source="assigned_agent.last_name", read_only=True
    )

    class Meta:
        model = Lead
        fields = [
            "id",
            "contact_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "assigned_agent_id",
            "assigned_agent_first_name",
            "assigned_agent_last_name",
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
    
    # Foreign Keys
    contact = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), required=False, allow_null=True
    )

    source = serializers.PrimaryKeyRelatedField(
        queryset=Source.objects.all(), required=False, allow_null=True
    )

    group = serializers.PrimaryKeyRelatedField(
        queryset=LeadGroup.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Lead
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "contact",
            "type",
            "status",
            "notes",
            "source",
            "group",
        ]

    # ---------------------------------
    # CREATE
    # ---------------------------------
    def create(self, validated_data):
        user = self.context["request"].user

        # Pull out relationship fields (already validated by PK field)
        contact = validated_data.pop("contact", None)
        source = validated_data.pop("source", None)
        group = validated_data.pop("group", None)

        lead = Lead.objects.create(
            assigned_agent=user,
            contact=contact,
            source=source,
            group=group,
            **validated_data
        )

        return lead

    # ---------------------------------
    # UPDATE
    # ---------------------------------
    def update(self, instance, validated_data):

        # Direct FK assignment — clean & safe
        if "contact" in validated_data:
            instance.contact = validated_data.pop("contact")

        if "source" in validated_data:
            instance.source = validated_data.pop("source")

        if "group" in validated_data:
            instance.group = validated_data.pop("group")

        # Simple fields
        for field in ["first_name", "last_name", "email", "phone", "type", "status", "notes"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance
