from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import AgentProfile


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _issue_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


# -------------------------------------------------------------------
# Serializers
# -------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        email = _normalize_email(value)
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError("Email already exists.")
        return email

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return value

    def create(self, validated_data):
        email = _normalize_email(validated_data["email"])
        return User.objects.create_user(
            username=email,
            email=email,
            first_name=validated_data["first_name"].strip(),
            last_name=validated_data.get("last_name", "").strip(),
            password=validated_data["password"],
        )


# -------------------------------------------------------------------
# REGISTER USER
# -------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def register_user(request):
    data = {
        "email": _normalize_email(request.data.get("email", "")),
        "first_name": request.data.get("first_name", "").strip(),
        "last_name": request.data.get("last_name", "").strip(),
        "password": request.data.get("password"),
    }

    if not data["email"]:
        return Response({"detail": "Email is required."}, status=400)
    if not data["first_name"]:
        return Response({"detail": "First name is required."}, status=400)
    if not data["password"]:
        return Response({"detail": "Password is required."}, status=400)

    serializer = RegisterSerializer(data=data)
    if not serializer.is_valid():
        errors = serializer.errors

        if "email" in errors and errors["email"] == ["Email already exists."]:
            return Response({"detail": "Email already exists."}, status=400)

        return Response({"detail": errors}, status=400)

    user = serializer.save()
    tokens = _issue_tokens(user)

    return Response(
        {**tokens, "user": UserSerializer(user).data},
        status=200,
    )


# -------------------------------------------------------------------
# LOGIN USER  (FINAL – TEST SUITE & REAL WORLD)
# -------------------------------------------------------------------


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get("email", "")
    password = request.data.get("password")

    if not email or not password:
        return Response({"detail": "Email and password are required."}, status=400)

    user = User.objects.filter(username=email).first()
    if not user:
        return Response({"detail": "Invalid email or password."}, status=401)

    if not user.check_password(password):
        return Response({"detail": "Invalid email or password."}, status=401)

    tokens = _issue_tokens(user)

    return Response(
        {
            "refresh": tokens["refresh"],
            "access": tokens["access"],
            "user": UserSerializer(user).data,
        },
        status=200,
    )


# -------------------------------------------------------------------
# CURRENT USER
# -------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    data = UserSerializer(request.user).data

    profile = AgentProfile.objects.filter(user=request.user).first()
    if profile:
        data["agent_profile_id"] = profile.id

    return Response(data, status=200)
