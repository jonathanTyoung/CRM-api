from rest_framework import serializers
from api.models import Contact, Tag, Source


# ---------------------------
# SUPPORTING SERIALIZERS
# ---------------------------

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ["id", "name"]


# ---------------------------
# READ SERIALIZER
# ---------------------------

class ContactSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    source = SourceSerializer(read_only=True)
    owner = serializers.CharField(source="owner.user.get_full_name", read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "notes",
            "owner",
            "source",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields  # everything is read-only


# ---------------------------
# WRITE SERIALIZER (CREATE + UPDATE)
# ---------------------------

class ContactCreateUpdateSerializer(serializers.ModelSerializer):

    # Related fields (IDs instead of nested)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    source_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Contact
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "notes",        # <-- Added correctly
            "source_id",
            "tag_ids",
        ]

    # ---------------------------
    # CREATE
    # ---------------------------
    def create(self, validated_data):
        tag_ids = validated_data.pop("tag_ids", [])
        source_id = validated_data.pop("source_id", None)

        contact = Contact.objects.create(
            owner=self.context["owner"],             # secure & correct
            source=self._get_source(source_id),
            **validated_data
        )

        self._set_tags(contact, tag_ids)
        return contact

    # ---------------------------
    # UPDATE
    # ---------------------------
    def update(self, instance, validated_data):
        tag_ids = validated_data.pop("tag_ids", None)
        source_id = validated_data.pop("source_id", None)

        # Set basic fields
        for field, value in validated_data.items():
            setattr(instance, field, value)

        # Set source
        if source_id is not None:
            instance.source = self._get_source(source_id)

        instance.save()

        # Update tags only if explicitly provided
        if tag_ids is not None:
            self._set_tags(instance, tag_ids)

        return instance

    # ---------------------------
    # HELPERS
    # ---------------------------
    def _get_source(self, source_id):
        """Return Source or None safely."""
        if not source_id:
            return None
        return Source.objects.filter(pk=source_id).first()

    def _set_tags(self, contact, tag_ids):
        """Set tags safely."""
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            contact.tags.set(tags)
        else:
            contact.tags.clear()
