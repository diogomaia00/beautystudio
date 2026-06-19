from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.services import selectors as services_selectors
from common.permissions import IsClient, IsStaffMember

from . import selectors, services
from .serializers import (
    BlacklistSerializer,
    ClientProfileUpdateSerializer,
    ClientSerializer,
    ClientServiceDurationSerializer,
    ClientServiceDurationWriteSerializer,
    OtpRequestSerializer,
    OtpVerifySerializer,
    StaffEducationSerializer,
    StaffEducationWriteSerializer,
    StaffPublicSerializer,
    UserSerializer,
)

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


# ============================================================
# Client app (/v1)
# ============================================================

class ClientProfileView(APIView):
    """The calling client's own profile (read + restricted update)."""

    permission_classes = [IsClient]

    @extend_schema(responses={200: UserSerializer}, tags=["clients"])
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    @extend_schema(request=ClientProfileUpdateSerializer, responses={200: UserSerializer}, tags=["clients"])
    def patch(self, request):
        data = ClientProfileUpdateSerializer(data=request.data, partial=True)
        data.is_valid(raise_exception=True)
        user = services.update_client_profile(client=request.user, **data.validated_data)
        return Response(UserSerializer(user).data)


class StaffPublicListView(APIView):
    """Public list of bookable staff with their education (experience page)."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    @extend_schema(responses={200: StaffPublicSerializer(many=True)}, tags=["staff-public"])
    def get(self, request):
        staff = selectors.list_staff(bookable_only=True).prefetch_related("educations")
        return Response(StaffPublicSerializer(staff, many=True).data)


class StaffPublicDetailView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]

    @extend_schema(responses={200: StaffPublicSerializer}, tags=["staff-public"])
    def get(self, request, staff_id):
        staff = selectors.get_staff(staff_id)
        if staff is None or not staff.is_active:
            raise NotFound("Staff member not found.")
        return Response(StaffPublicSerializer(staff).data)


# ============================================================
# Back office (/bo/v1)
# ============================================================

class BoStaffEducationListCreateView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: StaffEducationSerializer(many=True)}, tags=["bo-staff"])
    def get(self, request, staff_id):
        return Response(
            StaffEducationSerializer(
                selectors.list_staff_educations(staff_id), many=True
            ).data
        )

    @extend_schema(request=StaffEducationWriteSerializer, responses={201: StaffEducationSerializer}, tags=["bo-staff"])
    def post(self, request, staff_id):
        staff = selectors.get_staff(staff_id)
        if staff is None:
            raise NotFound("Staff member not found.")
        data = StaffEducationWriteSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        education = services.create_staff_education(staff=staff, **data.validated_data)
        return Response(
            StaffEducationSerializer(education).data, status=status.HTTP_201_CREATED
        )


class BoStaffEducationDetailView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(request=StaffEducationWriteSerializer, responses={200: StaffEducationSerializer}, tags=["bo-staff"])
    def patch(self, request, staff_id, education_id):
        education = selectors.get_staff_education(staff_id, education_id)
        if education is None:
            raise NotFound("Education record not found.")
        data = StaffEducationWriteSerializer(data=request.data, partial=True)
        data.is_valid(raise_exception=True)
        education = services.update_staff_education(education=education, **data.validated_data)
        return Response(StaffEducationSerializer(education).data)

    @extend_schema(responses={204: OpenApiResponse(description="Deleted")}, tags=["bo-staff"])
    def delete(self, request, staff_id, education_id):
        education = selectors.get_staff_education(staff_id, education_id)
        if education is None:
            raise NotFound("Education record not found.")
        services.delete_staff_education(education=education)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoClientListView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: ClientSerializer(many=True)}, tags=["bo-clients"])
    def get(self, request):
        clients = selectors.list_clients(search=request.query_params.get("search"))
        return Response(ClientSerializer(clients, many=True).data)


class BoClientDetailView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: ClientSerializer}, tags=["bo-clients"])
    def get(self, request, client_id):
        client = selectors.get_client(client_id)
        if client is None:
            raise NotFound("Client not found.")
        # Attendance history is derived from appointment status (see business-rules.md).
        from apps.appointments import selectors as appt_selectors

        data = ClientSerializer(client).data
        data["attendance"] = appt_selectors.get_client_attendance_summary(client_id)
        return Response(data)


class BoClientBlacklistView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(request=BlacklistSerializer, responses={200: ClientSerializer}, tags=["bo-clients"])
    def post(self, request, client_id):
        client = selectors.get_client(client_id)
        if client is None:
            raise NotFound("Client not found.")
        data = BlacklistSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        client = services.set_blacklisted(
            client=client, blacklisted=data.validated_data["blacklisted"]
        )
        return Response(ClientSerializer(client).data)


class BoClientDurationListCreateView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: ClientServiceDurationSerializer(many=True)}, tags=["bo-clients"])
    def get(self, request, client_id):
        return Response(
            ClientServiceDurationSerializer(
                selectors.list_client_service_durations(client_id), many=True
            ).data
        )

    @extend_schema(
        request=ClientServiceDurationWriteSerializer,
        responses={200: ClientServiceDurationSerializer},
        tags=["bo-clients"],
    )
    def post(self, request, client_id):
        client = selectors.get_client(client_id)
        if client is None:
            raise NotFound("Client not found.")
        data = ClientServiceDurationWriteSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        service = services_selectors.get_service(data.validated_data["service_id"])
        if service is None:
            raise NotFound("Service not found.")
        override = services.set_client_service_duration(
            client=client,
            service=service,
            duration_minutes=data.validated_data["duration_minutes"],
        )
        return Response(ClientServiceDurationSerializer(override).data)


class BoClientDurationDeleteView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={204: OpenApiResponse(description="Override cleared")}, tags=["bo-clients"])
    def delete(self, request, client_id, service_id):
        client = selectors.get_client(client_id)
        if client is None:
            raise NotFound("Client not found.")
        service = services_selectors.get_service(service_id)
        if service is None:
            raise NotFound("Service not found.")
        services.clear_client_service_duration(client=client, service=service)
        return Response(status=status.HTTP_204_NO_CONTENT)
