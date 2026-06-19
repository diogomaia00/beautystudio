from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from . import services
from .serializers import OtpRequestSerializer, OtpVerifySerializer, UserSerializer

# The session is established with the default model backend; OTP verifies the
# credential, the cookie carries the session afterwards (ADR 0002 & 0004).
AUTH_BACKEND = "django.contrib.auth.backends.ModelBackend"


@method_decorator(ensure_csrf_cookie, name="get")
class CsrfView(APIView):
    """Set the CSRF cookie so the SPA can send the token on unsafe methods."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiResponse(description="CSRF cookie set")}, tags=["auth"])
    def get(self, request):
        return Response({"detail": "CSRF cookie set"})


class OtpRequestView(APIView):
    """Request an SMS one-time code for login or sign-up."""

    authentication_classes: list = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp"

    @extend_schema(
        request=OtpRequestSerializer,
        responses={200: OpenApiResponse(description="Code sent if the request is valid")},
        tags=["auth"],
    )
    def post(self, request):
        serializer = OtpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.request_otp(**serializer.validated_data)
        return Response({"detail": "If the number is valid, a code has been sent."})


class OtpVerifyView(APIView):
    """Verify an SMS code and establish a session (login or sign-up)."""

    authentication_classes: list = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp"

    @extend_schema(request=OtpVerifySerializer, responses={200: UserSerializer}, tags=["auth"])
    def post(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        purpose = serializer.validated_data["purpose"]
        signup_data = serializer.signup_data() if purpose == "signup" else None
        user = services.verify_otp(
            msisdn=serializer.validated_data["msisdn"],
            code=serializer.validated_data["code"],
            purpose=purpose,
            signup_data=signup_data,
        )

        login(request, user, backend=AUTH_BACKEND)
        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    """End the current session."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={204: OpenApiResponse(description="Logged out")},
        tags=["auth"],
    )
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    """Return the currently authenticated user."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer}, tags=["auth"])
    def get(self, request):
        return Response(UserSerializer(request.user).data)
