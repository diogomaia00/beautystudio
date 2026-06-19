from __future__ import annotations

import datetime
from uuid import UUID

from django.db.models import QuerySet

from common.constants import CustomRequestStatus, WaitlistStatus
from common.utils import clinic_weekday

from .models import (
    CustomBookingRequest,
    StaffBreak,
    StaffSchedule,
    StaffTimeOff,
    Waitlist,
)


# ------------------------------------------------------------
# Schedules / breaks
# ------------------------------------------------------------

def list_schedules(staff_id: UUID) -> QuerySet[StaffSchedule]:
    return StaffSchedule.objects.filter(staff_id=staff_id)


def get_schedules_for_date(staff_id: UUID, on_date: datetime.date) -> QuerySet[StaffSchedule]:
    return StaffSchedule.objects.filter(
        staff_id=staff_id, weekday=clinic_weekday(on_date)
    ).order_by("start_time")


def list_breaks(staff_id: UUID) -> QuerySet[StaffBreak]:
    return StaffBreak.objects.filter(staff_id=staff_id)


def get_breaks_for_date(staff_id: UUID, on_date: datetime.date) -> QuerySet[StaffBreak]:
    return StaffBreak.objects.filter(
        staff_id=staff_id, weekday=clinic_weekday(on_date)
    ).order_by("start_time")


# ------------------------------------------------------------
# Time off
# ------------------------------------------------------------

def list_time_off(staff_id: UUID) -> QuerySet[StaffTimeOff]:
    return StaffTimeOff.objects.filter(staff_id=staff_id)


def list_time_off_overlapping(staff_id: UUID, start_at, end_at) -> QuerySet[StaffTimeOff]:
    """Time-off periods that overlap the half-open interval [start_at, end_at)."""
    return StaffTimeOff.objects.filter(
        staff_id=staff_id, start_at__lt=end_at, end_at__gt=start_at
    )


def is_on_time_off(staff_id: UUID, start_at, end_at) -> bool:
    return list_time_off_overlapping(staff_id, start_at, end_at).exists()


# ------------------------------------------------------------
# Waitlist / custom requests
# ------------------------------------------------------------

def list_waitlist(staff_id: UUID, *, status: str | None = WaitlistStatus.WAITING) -> QuerySet[Waitlist]:
    qs = Waitlist.objects.select_related("client", "service").filter(staff_id=staff_id)
    if status is not None:
        qs = qs.filter(status=status)
    return qs


def list_waitlist_for_time(staff_id: UUID, desired_start_at) -> QuerySet[Waitlist]:
    return Waitlist.objects.select_related("client", "service").filter(
        staff_id=staff_id,
        desired_start_at=desired_start_at,
        status=WaitlistStatus.WAITING,
    )


def list_custom_requests(staff_id: UUID, *, status: str | None = CustomRequestStatus.PENDING) -> QuerySet[CustomBookingRequest]:
    qs = CustomBookingRequest.objects.select_related("client", "service").filter(
        staff_id=staff_id
    )
    if status is not None:
        qs = qs.filter(status=status)
    return qs
