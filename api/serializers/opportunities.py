from rest_framework import serializers
from api.models import Contact, Opportunity, OpportunityContact
from api.serializers.opportunity_contact import OpportunityContactSerializer


class OpportunitySerializer(serializers.ModelSerializer):
    # MUST be writable or DRF drops the data
    participants = OpportunityContactSerializer(
        many=True, required=False, write_only=True
    )

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "title",
            "deal_type",
            "property_address",
            "mls_id",
            "stage",
            "price",
            "estimated_close_date",
            "notes",
            "participants",
            "assigned_agent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "assigned_agent"]

    # ------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------
    def validate(self, attrs):
        """
        Validate participants for both POST and PATCH.
        Ensures contact_id is present, coercible to int, and owned by the agent.
        """
        request_user = self.context["request"].user
        agent_profile = request_user.agent_profile

        participants = self.initial_data.get("participants", [])

        for item in participants:

            if "contact" not in item:
                raise serializers.ValidationError(
                    {"participants": "Each participant must include a 'contact' field."}
                )

            raw_contact = item["contact"]

            # Convert Contact object -> ID
            if hasattr(raw_contact, "id"):
                contact_id = raw_contact.id
            else:
                # Convert strings to int safely
                try:
                    contact_id = int(raw_contact)
                except (ValueError, TypeError):
                    raise serializers.ValidationError(
                        {"participants": f"Invalid contact id: {raw_contact}"}
                    )

            # Now validate existence AND ownership
            if not Contact.objects.filter(id=contact_id, owner=agent_profile).exists():
                raise serializers.ValidationError(
                    {
                        "participants": f"Contact {contact_id} does not belong to this agent."
                    }
                )

        return attrs

    # ------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------
    def create(self, validated_data):
        participants = self.initial_data.get("participants", [])

        request_user = self.context["request"].user
        agent_profile = request_user.agent_profile

        validated_data.pop("participants", None)
        validated_data.pop("assigned_agent", None)
        validated_data.pop("owner", None)

        opportunity = Opportunity.objects.create(
            owner=agent_profile,
            assigned_agent=agent_profile,
            **validated_data,
        )

        seen = set()
        for entry in participants:
            contact_id = entry.get("contact") or entry.get("contact_id")

            if hasattr(contact_id, "id"):
                contact_id = contact_id.id

            contact_id = int(contact_id)

            if contact_id in seen:
                continue
            seen.add(contact_id)

            OpportunityContact.objects.create(
                opportunity=opportunity,
                contact_id=contact_id,
                role=entry.get("role", ""),
            )

        return opportunity

    # ------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------
    def update(self, instance, validated_data):
        participants_data = self.initial_data.get("participants", None)

        # Update normal scalar fields
        for attr, value in validated_data.items():
            if attr == "participants":
                continue
            setattr(instance, attr, value)
        instance.save()

        # Replace participant list if provided
        if participants_data is not None:
            OpportunityContact.objects.filter(opportunity=instance).delete()

            seen = set()
            for entry in participants_data:
                raw = entry.get("contact") or entry.get("contact_id")

                if isinstance(raw, dict):
                    contact_id = raw.get("id")
                elif hasattr(raw, "id"):
                    contact_id = raw.id
                else:
                    contact_id = raw

                if not contact_id:
                    raise serializers.ValidationError(
                        {"participants": "Invalid contact format."}
                    )

                contact_id = int(contact_id)

                if contact_id in seen:
                    continue
                seen.add(contact_id)

                OpportunityContact.objects.create(
                    opportunity=instance,
                    contact_id=contact_id,
                    role=entry.get("role", ""),
                )

        return instance
