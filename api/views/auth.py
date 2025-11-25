from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle


# -------------------------
# USER SERIALIZER
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")


# -------------------------
# TEMP DISABLED REGISTER
# -------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def register_user(request):
    email = request.data.get("email", "").strip().lower()
    first_name = request.data.get("first_name", "").strip()
    last_name = request.data.get("last_name", "").strip()
    password = request.data.get("password")

    # --- VALIDATION ---
    if not email:
        return Response(
            {"error": "MISSING_EMAIL", "message": "Email is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not first_name:
        return Response(
            {"error": "MISSING_FIRST_NAME", "message": "First name is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not password:
        return Response(
            {"error": "MISSING_PASSWORD", "message": "Password is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=email).exists():
        return Response(
            {"detail": "Email already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --- CREATE USER ---
    user = User.objects.create_user(
        username=email,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
    )

    # --- ISSUE TOKENS ---
    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_200_OK,
    )


# -------------------------
# LOGIN (email-based)
# -------------------------
@api_view(["POST"])  # <-- REQUIRED DECORATOR (you were missing this)
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def login_user(request):
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "MISSING_FIELDS", "message": "Email and password required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=email, password=password)

    if not user:
        return Response(
            {"error": "INVALID_CREDENTIALS", "message": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        return Response(
            {"error": "ACCOUNT_DISABLED", "message": "This account is disabled."},
            status=status.HTTP_403_FORBIDDEN,
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }
    )


# -------------------------
# CURRENT USER
# -------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response(UserSerializer(request.user).data)
