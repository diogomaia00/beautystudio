from __future__ import annotations

import datetime
from uuid import UUID

from django.db.models import QuerySet
from django.utils import timezone

from common.constants import AppointmentStatus
from common.utils import clinic_tz

from .models import Appointment


def get_appointment(appointment_id: UUID) -> Appointment | None:
    return (
        Appointment.objects.select_related("client", "staff", "service")
        .filter(pk=appointment_id)
        .first()
    )


def list_client_appointments(
    client_id: UUID, *, statuses: list[str] | None = None
) -> QuerySet[Appointment]:
    qs = Appointment.objects.select_related("staff", "service").filter(client_id=client_id)
    if statuses:
        qs = qs.filter(status__in=statuses)
    return qs


def list_staff_appointments_in_range(staff_id: UUID, start_at, end_at) -> QuerySet[Appointment]:
    """Appointments for a staff member overlapping [start_at, end_at) (BO calendar)."""
    return (
        Appointment.objects.select_related("client", "service")
        .filter(staff_id=staff_id, start_at__lt=end_at, end_at__gt=start_at)
        .exclude(status=AppointmentStatus.CANCELED)
    )


def list_active_appointments_in_range(staff_id: UUID, start_at, end_at) -> QuerySet[Appointment]:
    """Booked (time-occupying) appointments overlapping a range — feeds slot generation."""
    return Appointment.objects.filter(
        staff_id=staff_id,
        status=AppointmentStatus.BOOKED,
        start_at__lt=end_at,
        end_at__gt=start_at,
    )


def has_overlapping_appointment(staff_id: UUID, start_at, end_at, *, exclude_id: UUID | None = None) -> bool:
    qs = Appointment.objects.filter(
        staff_id=staff_id,
        status=AppointmentStatus.BOOKED,
        start_at__lt=end_at,
        end_at__gt=start_at,
    )
    if exclude_id is not None:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()


def _local_day_bounds_utc(day: datetime.date):
    tz = clinic_tz()
    start_local = datetime.datetime.combine(day, datetime.time.min, tzinfo=tz)
    return start_local, start_local + datetime.timedelta(days=1)


def count_client_appointments_on_day(client_id: UUID, day: datetime.date) -> int:
    """Active (booked/made) appointment count for a client on a local day."""
    start_local, end_local = _local_day_bounds_utc(day)
    return (
        Appointment.objects.filter(
            client_id=client_id,
            start_at__gte=start_local,
            start_at__lt=end_local,
        )
        .exclude(status=AppointmentStatus.CANCELED)
        .count()
    )


def count_client_appointments_in_week(client_id: UUID, day: datetime.date) -> int:
    """Active appointment count for a client in the local ISO week containing ``day``."""
    tz = clinic_tz()
    monday = day - datetime.timedelta(days=day.weekday())
    week_start = datetime.datetime.combine(monday, datetime.time.min, tzinfo=tz)
    week_end = week_start + datetime.timedelta(days=7)
    return (
        Appointment.objects.filter(
            client_id=client_id,
            start_at__gte=week_start,
            start_at__lt=week_end,
        )
        .exclude(status=AppointmentStatus.CANCELED)
        .count()
    )


def get_client_attendance_summary(client_id: UUID) -> dict:
    """Attendance history derived from appointment status (see business-rules.md)."""
    qs = Appointment.objects.filter(client_id=client_id)
    return {
        "booked": qs.filter(status=AppointmentStatus.BOOKED).count(),
        "made": qs.filter(status=AppointmentStatus.MADE).count(),
        "canceled": qs.filter(status=AppointmentStatus.CANCELED).count(),
        "no_show": qs.filter(status=AppointmentStatus.NO_SHOW).count(),
    }


def get_idempotent_appointment(idempotency_key: str) -> Appointment | None:
    return Appointment.objects.filter(idempotency_key=idempotency_key).first()


def list_booked_appointments_on_local_date(day: datetime.date) -> QuerySet[Appointment]:
    """Booked appointments starting on a given local day (feeds reminders)."""
    start_local, end_local = _local_day_bounds_utc(day)
    return Appointment.objects.select_related("client", "service").filter(
        status=AppointmentStatus.BOOKED,
        start_at__gte=start_local,
        start_at__lt=end_local,
    )


def local_month_bounds(year: int, month: int):
    """Return [start, end) datetimes (UTC) for a local calendar month."""
    tz = clinic_tz()
    start_local = datetime.datetime(year, month, 1, tzinfo=tz)
    if month == 12:
        end_local = datetime.datetime(year + 1, 1, 1, tzinfo=tz)
    else:
        end_local = datetime.datetime(year, month + 1, 1, tzinfo=tz)
    return start_local, end_local


def list_staff_appointments_in_local_month(staff_id: UUID, year: int, month: int) -> QuerySet[Appointment]:
    """All appointments for a staff member starting within a local month."""
    start_at, end_at = local_month_bounds(year, month)
    return Appointment.objects.select_related("service", "client").filter(
        staff_id=staff_id, start_at__gte=start_at, start_at__lt=end_at
    )


def client_ids_with_made_before(staff_id: UUID, before) -> set:
    """Client ids that already had a made appointment with this staff before ``before``."""
    return set(
        Appointment.objects.filter(
            staff_id=staff_id, status=AppointmentStatus.MADE, start_at__lt=before
        ).values_list("client_id", flat=True)
    )
