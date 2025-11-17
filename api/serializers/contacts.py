from rest_framework import serializers
from api.models import Contact, Tag, Source, AgentProfile


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
    """Serializer used for GET requests."""

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
            "owner",
            "source",
            "tags",
            "created_at",
            "updated_at",
        ]


# ---------------------------
# WRITE SERIALIZER
# ---------------------------
class ContactCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for POST/PUT
    Accepts tag_ids and source_id
    """

    tag_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    source_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Contact
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "source_id",
            "tag_ids",
        ]

    def create(self, validated_data):
        tag_ids = validated_data.pop("tag_ids", [])
        source_id = validated_data.pop("source_id", None)

        # Get owner injected from ViewSet perform_create()
        owner: AgentProfile = validated_data.pop("owner")

        contact = Contact.objects.create(
            owner=owner,
            source=Source.objects.get(pk=source_id) if source_id else None,
            **validated_data
        )

        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            contact.tags.set(tags)

        return contact

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop("tag_ids", None)
        source_id = validated_data.pop("source_id", None)

        # Update basic fields
        for field, value in validated_data.items():
            setattr(instance, field, value)

        if source_id:
            instance.source = Source.objects.get(pk=source_id)

        instance.save()

        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            instance.tags.set(tags)

        return instance
