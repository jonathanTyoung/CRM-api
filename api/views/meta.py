from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Tag, Source
from api.serializers.contacts import TagSerializer, SourceSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_tags(request):
    tags = Tag.objects.all()
    return Response(TagSerializer(tags, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_sources(request):
    sources = Source.objects.all()
    return Response(SourceSerializer(sources, many=True).data)
