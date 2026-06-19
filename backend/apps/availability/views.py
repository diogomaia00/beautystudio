from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.services import selectors as services_selectors
from apps.users import selectors as users_selectors
from common.constants import NAIL_ART_EXTRA_MINUTES, NailArtOption, UserRole
from common.permissions import IsClient, IsStaffMember

from . import selectors, services
from .serializers import (
    CustomBookingRequestSerializer,
    CustomRequestCreateSerializer,
    SlotQuerySerializer,
    StaffBreakSerializer,
    StaffScheduleSerializer,
    StaffTimeOffSerializer,
    StatusUpdateSerializer,
    WaitlistJoinSerializer,
    WaitlistSerializer,
    WeeklyScheduleWriteSerializer,
)


# ============================================================
# Client app (/v1)
# ============================================================

class AvailableSlotsView(APIView):
    """Dynamically generated bookable start times for a staff + service + date.

    Server-side source of truth — the frontend calendar must not be trusted for
    availability (see frontend.md). Returns ISO-8601 UTC start times.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[SlotQuerySerializer],
        responses={200: OpenApiResponse(description="{'slots': [iso8601, ...]}")},
        tags=["availability"],
    )
    def get(self, request):
        query = SlotQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        params = query.validated_data

        staff = users_selectors.get_staff(params["staff_id"])
        if staff is None or not staff.is_active:
            raise NotFound("Staff member not found.")
        service = services_selectors.get_service(params["service_id"])
        if service is None or service.staff_id != staff.id:
            raise NotFound("Service not found for this staff member.")

        duration = _effective_duration(request.user, service, params.get("nail_art"))
        slots = services.generate_slots(
            staff=staff, on_date=params["date"], duration_minutes=duration
        )
        return Response({"slots": [s.isoformat() for s in slots]})


def _effective_duration(user, service, nail_art_option) -> int:
    """Service default, overridden per-client, plus any Nail Art add-on minutes."""
    duration = service.duration_minutes
    if getattr(user, "is_authenticated", False) and getattr(user, "role", None) == UserRole.CLIENT:
        override = users_selectors.get_client_service_duration(user.id, service.id)
        if override is not None:
            duration = override
    if nail_art_option and service.is_nail_service:
        duration += NAIL_ART_EXTRA_MINUTES[NailArtOption(nail_art_option)]
    return duration


class WaitlistJoinView(APIView):
    permission_classes = [IsClient]

    @extend_schema(request=WaitlistJoinSerializer, responses={201: WaitlistSerializer}, tags=["availability"])
    def post(self, request):
        data = WaitlistJoinSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        service = services_selectors.get_service(data.validated_data["service_id"])
        if service is None:
            raise NotFound("Service not found.")
        entry = services.join_waitlist(
            client=request.user,
            service=service,
            desired_start_at=data.validated_data["desired_start_at"],
            note=data.validated_data["note"],
        )
        return Response(WaitlistSerializer(entry).data, status=status.HTTP_201_CREATED)


class CustomRequestCreateView(APIView):
    permission_classes = [IsClient]

    @extend_schema(
        request=CustomRequestCreateSerializer,
        responses={201: CustomBookingRequestSerializer},
        tags=["availability"],
    )
    def post(self, request):
        data = CustomRequestCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        service = services_selectors.get_service(data.validated_data["service_id"])
        if service is None:
            raise NotFound("Service not found.")
        req = services.create_custom_request(
            client=request.user,
            service=service,
            preferred_date=data.validated_data["preferred_date"],
            preferred_time=data.validated_data.get("preferred_time"),
            note=data.validated_data["note"],
        )
        return Response(
            CustomBookingRequestSerializer(req).data, status=status.HTTP_201_CREATED
        )


# ============================================================
# Back office (/bo/v1)
# ============================================================

class BoStaffScheduleView(APIView):
    permission_classes = [IsStaffMember]

    def _staff(self, staff_id):
        staff = users_selectors.get_staff(staff_id)
        if staff is None:
            raise NotFound("Staff member not found.")
        return staff

    @extend_schema(responses={200: StaffScheduleSerializer(many=True)}, tags=["bo-availability"])
    def get(self, request, staff_id):
        return Response(
            StaffScheduleSerializer(selectors.list_schedules(staff_id), many=True).data
        )

    @extend_schema(request=WeeklyScheduleWriteSerializer, responses={200: StaffScheduleSerializer(many=True)}, tags=["bo-availability"])
    def put(self, request, staff_id):
        staff = self._staff(staff_id)
        data = WeeklyScheduleWriteSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        created = services.replace_weekly_schedule(
            staff=staff, entries=data.validated_data["entries"]
        )
        return Response(StaffScheduleSerializer(created, many=True).data)


class BoStaffBreakView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: StaffBreakSerializer(many=True)}, tags=["bo-availability"])
    def get(self, request, staff_id):
        return Response(StaffBreakSerializer(selectors.list_breaks(staff_id), many=True).data)

    @extend_schema(request=StaffBreakSerializer, responses={201: StaffBreakSerializer}, tags=["bo-availability"])
    def post(self, request, staff_id):
        staff = users_selectors.get_staff(staff_id)
        if staff is None:
            raise NotFound("Staff member not found.")
        data = StaffBreakSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        brk = services.add_break(staff=staff, **data.validated_data)
        return Response(StaffBreakSerializer(brk).data, status=status.HTTP_201_CREATED)


class BoStaffBreakDeleteView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={204: OpenApiResponse(description="Deleted")}, tags=["bo-availability"])
    def delete(self, request, staff_id, break_id):
        brk = selectors.list_breaks(staff_id).filter(pk=break_id).first()
        if brk is None:
            raise NotFound("Break not found.")
        services.delete_break(brk=brk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoStaffTimeOffView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: StaffTimeOffSerializer(many=True)}, tags=["bo-availability"])
    def get(self, request, staff_id):
        return Response(StaffTimeOffSerializer(selectors.list_time_off(staff_id), many=True).data)

    @extend_schema(request=StaffTimeOffSerializer, responses={201: StaffTimeOffSerializer}, tags=["bo-availability"])
    def post(self, request, staff_id):
        staff = users_selectors.get_staff(staff_id)
        if staff is None:
            raise NotFound("Staff member not found.")
        data = StaffTimeOffSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        time_off = services.add_time_off(staff=staff, **data.validated_data)
        return Response(StaffTimeOffSerializer(time_off).data, status=status.HTTP_201_CREATED)


class BoStaffTimeOffDeleteView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={204: OpenApiResponse(description="Deleted")}, tags=["bo-availability"])
    def delete(self, request, staff_id, time_off_id):
        time_off = selectors.list_time_off(staff_id).filter(pk=time_off_id).first()
        if time_off is None:
            raise NotFound("Time-off not found.")
        services.delete_time_off(time_off=time_off)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoWaitlistView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: WaitlistSerializer(many=True)}, tags=["bo-availability"])
    def get(self, request, staff_id):
        return Response(
            WaitlistSerializer(
                selectors.list_waitlist(
                    staff_id, status=request.query_params.get("status", "waiting") or None
                ),
                many=True,
            ).data
        )


class BoWaitlistUpdateView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(request=StatusUpdateSerializer, responses={200: WaitlistSerializer}, tags=["bo-availability"])
    def patch(self, request, staff_id, waitlist_id):
        entry = selectors.list_waitlist(staff_id, status=None).filter(pk=waitlist_id).first()
        if entry is None:
            raise NotFound("Waitlist entry not found.")
        data = StatusUpdateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        entry = services.update_waitlist_status(entry=entry, status=data.validated_data["status"])
        return Response(WaitlistSerializer(entry).data)


class BoCustomRequestView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: CustomBookingRequestSerializer(many=True)}, tags=["bo-availability"])
    def get(self, request, staff_id):
        return Response(
            CustomBookingRequestSerializer(
                selectors.list_custom_requests(
                    staff_id, status=request.query_params.get("status", "pending") or None
                ),
                many=True,
            ).data
        )


class BoCustomRequestUpdateView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(request=StatusUpdateSerializer, responses={200: CustomBookingRequestSerializer}, tags=["bo-availability"])
    def patch(self, request, staff_id, request_id):
        req = selectors.list_custom_requests(staff_id, status=None).filter(pk=request_id).first()
        if req is None:
            raise NotFound("Custom request not found.")
        data = StatusUpdateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        req = services.update_custom_request_status(request=req, status=data.validated_data["status"])
        return Response(CustomBookingRequestSerializer(req).data)
