from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.services import selectors as services_selectors
from common.constants import CancelReason
from common.permissions import IsClient, IsStaffMember

from . import selectors, services
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    BatchCreateSerializer,
    BoAppointmentSerializer,
    NailArtEditSerializer,
    RescheduleSerializer,
)


def _require_service(service_id):
    service = services_selectors.get_service(service_id)
    if service is None:
        raise NotFound("Service not found.")
    return service


# ============================================================
# Client app (/v1/appointments/)
# ============================================================

class AppointmentListCreateView(APIView):
    permission_classes = [IsClient]

    @extend_schema(responses={200: AppointmentSerializer(many=True)}, tags=["appointments"])
    def get(self, request):
        statuses = request.query_params.getlist("status") or None
        qs = selectors.list_client_appointments(request.user.id, statuses=statuses)
        return Response(AppointmentSerializer(qs, many=True).data)

    @extend_schema(request=AppointmentCreateSerializer, responses={201: AppointmentSerializer}, tags=["appointments"])
    def post(self, request):
        data = AppointmentCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        service = _require_service(data.validated_data["service_id"])
        appointment = services.create_appointment(
            client=request.user,
            service=service,
            start_at=data.validated_data["start_at"],
            nail_art_option=data.validated_data.get("nail_art_option"),
            notes=data.validated_data["notes"],
            idempotency_key=data.validated_data.get("idempotency_key"),
        )
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)


class BatchCreateView(APIView):
    permission_classes = [IsClient]

    @extend_schema(request=BatchCreateSerializer, responses={201: AppointmentSerializer(many=True)}, tags=["appointments"])
    def post(self, request):
        data = BatchCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        items = []
        for item in data.validated_data["items"]:
            items.append(
                {
                    "service": _require_service(item["service_id"]),
                    "start_at": item["start_at"],
                    "nail_art_option": item.get("nail_art_option"),
                    "notes": item.get("notes", ""),
                }
            )
        _, created = services.create_batch(
            client=request.user,
            items=items,
            idempotency_key=data.validated_data.get("idempotency_key"),
        )
        return Response(AppointmentSerializer(created, many=True).data, status=status.HTTP_201_CREATED)


class _ClientAppointmentBase(APIView):
    permission_classes = [IsClient]

    def get_owned(self, request, appointment_id):
        appointment = selectors.get_appointment(appointment_id)
        if appointment is None:
            raise NotFound("Appointment not found.")
        if appointment.client_id != request.user.id:
            raise PermissionDenied("This appointment is not yours.")
        return appointment


class AppointmentDetailView(_ClientAppointmentBase):
    @extend_schema(responses={200: AppointmentSerializer}, tags=["appointments"])
    def get(self, request, appointment_id):
        return Response(AppointmentSerializer(self.get_owned(request, appointment_id)).data)


class AppointmentCancelView(_ClientAppointmentBase):
    @extend_schema(request=None, responses={200: AppointmentSerializer}, tags=["appointments"])
    def post(self, request, appointment_id):
        appointment = self.get_owned(request, appointment_id)
        appointment = services.cancel_appointment(
            appointment=appointment, reason=CancelReason.CLIENT
        )
        return Response(AppointmentSerializer(appointment).data)


class AppointmentRescheduleView(_ClientAppointmentBase):
    @extend_schema(request=RescheduleSerializer, responses={200: AppointmentSerializer}, tags=["appointments"])
    def post(self, request, appointment_id):
        appointment = self.get_owned(request, appointment_id)
        data = RescheduleSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        appointment = services.reschedule_appointment(
            appointment=appointment,
            new_start_at=data.validated_data["new_start_at"],
            by_client=True,
        )
        return Response(AppointmentSerializer(appointment).data)


class AppointmentNailArtBlockedView(_ClientAppointmentBase):
    """Clients cannot switch Nail Art simple↔complex — only staff can.

    The client app surfaces a modal telling the client to talk to the staff
    member; this endpoint enforces the same rule server-side (see business-rules.md).
    """

    @extend_schema(
        request=None,
        responses={403: OpenApiResponse(description="Staff-only change")},
        tags=["appointments"],
    )
    def post(self, request, appointment_id):
        self.get_owned(request, appointment_id)
        raise PermissionDenied(
            "Nail Art changes are made by the staff member — please talk to them directly."
        )


# ============================================================
# Back office (/bo/v1/appointments/)
# ============================================================

class BoAppointmentListView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: BoAppointmentSerializer(many=True)}, tags=["bo-appointments"])
    def get(self, request):
        staff_id = request.query_params.get("staff_id")
        start_at = request.query_params.get("start_at")
        end_at = request.query_params.get("end_at")
        if not (staff_id and start_at and end_at):
            raise NotFound("staff_id, start_at and end_at query params are required.")
        qs = selectors.list_staff_appointments_in_range(staff_id, start_at, end_at)
        return Response(BoAppointmentSerializer(qs, many=True).data)


class _BoAppointmentBase(APIView):
    permission_classes = [IsStaffMember]

    def get_appointment(self, appointment_id):
        appointment = selectors.get_appointment(appointment_id)
        if appointment is None:
            raise NotFound("Appointment not found.")
        return appointment


class BoAppointmentDetailView(_BoAppointmentBase):
    @extend_schema(responses={200: BoAppointmentSerializer}, tags=["bo-appointments"])
    def get(self, request, appointment_id):
        return Response(BoAppointmentSerializer(self.get_appointment(appointment_id)).data)


class BoAppointmentMarkMadeView(_BoAppointmentBase):
    @extend_schema(request=None, responses={200: BoAppointmentSerializer}, tags=["bo-appointments"])
    def post(self, request, appointment_id):
        appointment = services.mark_made(appointment=self.get_appointment(appointment_id))
        return Response(BoAppointmentSerializer(appointment).data)


class BoAppointmentMarkNoShowView(_BoAppointmentBase):
    @extend_schema(request=None, responses={200: BoAppointmentSerializer}, tags=["bo-appointments"])
    def post(self, request, appointment_id):
        appointment = services.mark_no_show(appointment=self.get_appointment(appointment_id))
        return Response(BoAppointmentSerializer(appointment).data)


class BoAppointmentCancelView(_BoAppointmentBase):
    @extend_schema(request=None, responses={200: BoAppointmentSerializer}, tags=["bo-appointments"])
    def post(self, request, appointment_id):
        appointment = services.cancel_appointment(
            appointment=self.get_appointment(appointment_id), reason=CancelReason.STAFF
        )
        return Response(BoAppointmentSerializer(appointment).data)


class BoAppointmentRescheduleView(_BoAppointmentBase):
    @extend_schema(request=RescheduleSerializer, responses={200: BoAppointmentSerializer}, tags=["bo-appointments"])
    def post(self, request, appointment_id):
        data = RescheduleSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        appointment = services.reschedule_appointment(
            appointment=self.get_appointment(appointment_id),
            new_start_at=data.validated_data["new_start_at"],
            by_client=False,
        )
        return Response(BoAppointmentSerializer(appointment).data)


class BoAppointmentNailArtView(_BoAppointmentBase):
    @extend_schema(request=NailArtEditSerializer, responses={200: BoAppointmentSerializer}, tags=["bo-appointments"])
    def patch(self, request, appointment_id):
        data = NailArtEditSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        appointment = services.edit_nail_art(
            appointment=self.get_appointment(appointment_id),
            nail_art_option=data.validated_data["nail_art_option"],
        )
        return Response(BoAppointmentSerializer(appointment).data)
