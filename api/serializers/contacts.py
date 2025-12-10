from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Contact, Tag, Source


# ---------------------------------------
# SUPPORTING SERIALIZERS
# ---------------------------------------


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ["id", "name"]


# ---------------------------------------
# READ SERIALIZER (NESTED, SAFE)
# ---------------------------------------


class ContactSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    source = SourceSerializer(read_only=True)
    owner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "notes",
            "relationship_type",
            "owner",
            "source",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_owner(self, obj):
        """Return useful structured owner info."""
        user = obj.owner.user

        return {
            "id": user.id,
            "name": user.get_full_name() or user.username or user.email,
            "email": user.email,
        }


# ---------------------------------------
# WRITE SERIALIZER (CREATE + UPDATE)
# ---------------------------------------

class ContactCreateUpdateSerializer(serializers.ModelSerializer):
    tag_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    source_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Contact
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "notes",
            "relationship_type",
            "source_id",
            "tag_ids",
        ]

    def create(self, validated_data):
        tag_ids = validated_data.pop("tag_ids", [])
        source_id = validated_data.pop("source_id", None)

        # Owner ALWAYS comes from logged-in agent
        agent_profile = self.context["request"].user.agent_profile

        contact = Contact.objects.create(
            owner=agent_profile, source=self._get_source(source_id), **validated_data
        )

        self._set_tags(contact, tag_ids)
        return contact

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop("tag_ids", None)
        source_id = validated_data.pop("source_id", None)

        # Primitive fields
        for field, value in validated_data.items():
            setattr(instance, field, value)

        # Update source
        if source_id is not None:
            instance.source = self._get_source(source_id)

        instance.save()

        # Update tags ONLY if tag_ids provided
        if tag_ids is not None:
            self._set_tags(instance, tag_ids)

        return instance

    # -------------------------
    # Helpers
    # -------------------------

    def _get_source(self, source_id):
        if not source_id:
            return None
        return Source.objects.filter(id=source_id).first()

    def _set_tags(self, contact, tag_ids):
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            contact.tags.set(tags)
        else:
            contact.tags.clear()
