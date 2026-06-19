from __future__ import annotations

import datetime
from datetime import timedelta, timezone as dt_timezone
from typing import Iterable

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.core.selectors import get_system_settings
from common.constants import CustomRequestStatus, WaitlistStatus
from common.utils import clinic_tz

from . import selectors
from .models import (
    CustomBookingRequest,
    StaffBreak,
    StaffSchedule,
    StaffTimeOff,
    Waitlist,
)


def _overlaps(a_start, a_end, b_start, b_end) -> bool:
    """True if the half-open intervals [a_start, a_end) and [b_start, b_end) overlap."""
    return a_start < b_end and a_end > b_start


# ------------------------------------------------------------
# Dynamic slot generation (see database.md — slots are never stored)
# ------------------------------------------------------------

def generate_slots(
    *,
    staff,
    on_date: datetime.date,
    duration_minutes: int,
    now=None,
) -> list[datetime.datetime]:
    """Return bookable start times (UTC) for ``staff`` on ``on_date``.

    Generated dynamically from the staff weekly schedule, minus breaks, time-off,
    and existing appointments, at ``booking_slot_minutes`` granularity. A slot is
    valid only if a ``duration_minutes`` block fits inside a working window and
    respects the ``minimum_notice_hours`` lead time. Never persisted.
    """
    settings_row = get_system_settings()
    step = timedelta(minutes=settings_row.booking_slot_minutes)
    duration = timedelta(minutes=duration_minutes)
    now = now or timezone.now()
    earliest = now + timedelta(hours=settings_row.minimum_notice_hours)
    tz = clinic_tz()

    schedules = list(selectors.get_schedules_for_date(staff.id, on_date))
    if not schedules:
        return []
    breaks = list(selectors.get_breaks_for_date(staff.id, on_date))

    # Bound the existing-appointment lookup to this local day (converted to UTC).
    day_start_utc = datetime.datetime.combine(on_date, datetime.time.min, tzinfo=tz).astimezone(
        dt_timezone.utc
    )
    day_end_utc = (
        datetime.datetime.combine(on_date, datetime.time.min, tzinfo=tz) + timedelta(days=1)
    ).astimezone(dt_timezone.utc)

    from apps.appointments import selectors as appt_selectors

    busy = list(
        appt_selectors.list_active_appointments_in_range(staff.id, day_start_utc, day_end_utc)
    )

    slots: list[datetime.datetime] = []
    for window in schedules:
        win_start = datetime.datetime.combine(on_date, window.start_time, tzinfo=tz)
        win_end = datetime.datetime.combine(on_date, window.end_time, tzinfo=tz)
        candidate = win_start
        while candidate + duration <= win_end:
            cand_end = candidate + duration
            start_utc = candidate.astimezone(dt_timezone.utc)
            end_utc = cand_end.astimezone(dt_timezone.utc)

            if start_utc < earliest:
                candidate += step
                continue
            if any(
                _overlaps(
                    candidate,
                    cand_end,
                    datetime.datetime.combine(on_date, b.start_time, tzinfo=tz),
                    datetime.datetime.combine(on_date, b.end_time, tzinfo=tz),
                )
                for b in breaks
            ):
                candidate += step
                continue
            if selectors.is_on_time_off(staff.id, start_utc, end_utc):
                candidate += step
                continue
            if any(_overlaps(start_utc, end_utc, a.start_at, a.end_at) for a in busy):
                candidate += step
                continue

            slots.append(start_utc)
            candidate += step

    return sorted(slots)


# ------------------------------------------------------------
# Schedule management (BO)
# ------------------------------------------------------------

def _validate_window(start_time, end_time) -> None:
    if end_time <= start_time:
        raise ValidationError("End time must be after start time.")


def _validate_weekday(weekday: int) -> None:
    if not 1 <= weekday <= 7:
        raise ValidationError("weekday must be between 1 (Sun) and 7 (Sat).")


@transaction.atomic
def replace_weekly_schedule(*, staff, entries: Iterable[dict]) -> list[StaffSchedule]:
    """Replace a staff member's entire weekly schedule with ``entries``."""
    StaffSchedule.objects.filter(staff=staff).delete()
    created: list[StaffSchedule] = []
    for entry in entries:
        _validate_weekday(entry["weekday"])
        _validate_window(entry["start_time"], entry["end_time"])
        created.append(
            StaffSchedule.objects.create(
                staff=staff,
                weekday=entry["weekday"],
                start_time=entry["start_time"],
                end_time=entry["end_time"],
            )
        )
    return created


@transaction.atomic
def add_break(*, staff, weekday: int, start_time, end_time, reason: str = "") -> StaffBreak:
    _validate_weekday(weekday)
    _validate_window(start_time, end_time)
    return StaffBreak.objects.create(
        staff=staff, weekday=weekday, start_time=start_time, end_time=end_time, reason=reason
    )


@transaction.atomic
def delete_break(*, brk: StaffBreak) -> None:
    brk.delete()


@transaction.atomic
def add_time_off(*, staff, start_at, end_at, reason: str = "") -> StaffTimeOff:
    if end_at <= start_at:
        raise ValidationError("Time-off end must be after its start.")
    return StaffTimeOff.objects.create(
        staff=staff, start_at=start_at, end_at=end_at, reason=reason
    )


@transaction.atomic
def delete_time_off(*, time_off: StaffTimeOff) -> None:
    time_off.delete()


# ------------------------------------------------------------
# Waitlist
# ------------------------------------------------------------

@transaction.atomic
def join_waitlist(*, client, service, desired_start_at, note: str = "") -> Waitlist:
    """Add a client to the waitlist for an occupied time and alert the staff member."""
    if desired_start_at <= timezone.now():
        raise ValidationError("The desired time must be in the future.")
    entry = Waitlist.objects.create(
        client=client,
        staff=service.staff,
        service=service,
        desired_start_at=desired_start_at,
        note=note,
    )
    # BO alert (deferred) — staff contact the client outside the app (v1).
    from apps.notifications import services as notifications

    notifications.notify_staff_waitlist_join(waitlist=entry)
    return entry


@transaction.atomic
def update_waitlist_status(*, entry: Waitlist, status: str) -> Waitlist:
    if status not in WaitlistStatus.values:
        raise ValidationError("Invalid waitlist status.")
    entry.status = status
    entry.save(update_fields=["status", "updated_at"])
    return entry


# ------------------------------------------------------------
# Custom booking requests (beyond the horizon)
# ------------------------------------------------------------

@transaction.atomic
def create_custom_request(
    *, client, service, preferred_date, preferred_time=None, note: str = ""
) -> CustomBookingRequest:
    """Create a custom booking request (beyond the horizon) and alert the staff member."""
    request = CustomBookingRequest.objects.create(
        client=client,
        staff=service.staff,
        service=service,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
        note=note,
    )
    from apps.notifications import services as notifications

    notifications.notify_staff_custom_request(custom_request=request)
    return request


@transaction.atomic
def update_custom_request_status(*, request: CustomBookingRequest, status: str) -> CustomBookingRequest:
    if status not in CustomRequestStatus.values:
        raise ValidationError("Invalid request status.")
    request.status = status
    request.save(update_fields=["status", "updated_at"])
    return request
