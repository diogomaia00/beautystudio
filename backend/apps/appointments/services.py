from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.availability import selectors as availability_selectors
from apps.core.selectors import get_system_settings
from apps.services import services as services_layer
from apps.users import selectors as users_selectors
from common.constants import (
    NAIL_ART_EXTRA_MINUTES,
    AppointmentStatus,
    CancelReason,
    NailArtOption,
)
from common.utils import clinic_tz

from . import selectors
from .models import Appointment, AppointmentBatch

# Self-service cancel/reschedule cutoff (business-rules.md).
SELF_SERVICE_CUTOFF_HOURS = 24


# ------------------------------------------------------------
# Derived values
# ------------------------------------------------------------

def _compute_duration(client, service, nail_art_option) -> int:
    """Per-client override (else service default) plus any Nail Art add-on minutes."""
    base = users_selectors.get_client_service_duration(client.id, service.id)
    if base is None:
        base = service.duration_minutes
    if nail_art_option and service.is_nail_service:
        base += NAIL_ART_EXTRA_MINUTES[NailArtOption(nail_art_option)]
    return base


def _snapshot_price(service):
    """The effective (discounted) price + quote-only flag, frozen at booking time."""
    return services_layer.effective_price(service), service.is_quote_only


def _within_cutoff(start_at) -> bool:
    return timezone.now() + timedelta(hours=SELF_SERVICE_CUTOFF_HOURS) > start_at


# ------------------------------------------------------------
# Validation (server is the source of truth — see database.md / frontend.md)
# ------------------------------------------------------------

def _validate_booking_window(start_at, settings_row, now) -> None:
    if start_at <= now:
        raise ValidationError("Cannot book a time in the past.")
    if start_at < now + timedelta(hours=settings_row.minimum_notice_hours):
        raise ValidationError(
            f"Bookings require at least {settings_row.minimum_notice_hours}h notice."
        )
    if start_at > now + timedelta(days=settings_row.booking_horizon_days):
        raise ValidationError(
            "That date is beyond the booking horizon — please use a custom request."
        )


def _validate_within_schedule(staff, start_at, end_at) -> None:
    tz = clinic_tz()
    start_local = start_at.astimezone(tz)
    end_local = end_at.astimezone(tz)
    if start_local.date() != end_local.date():
        raise ValidationError("An appointment must fall within a single day.")

    day = start_local.date()
    windows = list(availability_selectors.get_schedules_for_date(staff.id, day))
    fits = any(
        w.start_time <= start_local.time() and end_local.time() <= w.end_time for w in windows
    )
    if not fits:
        raise ValidationError("Outside the staff member's working hours.")

    for brk in availability_selectors.get_breaks_for_date(staff.id, day):
        if start_local.time() < brk.end_time and end_local.time() > brk.start_time:
            raise ValidationError("That time overlaps a break window.")

    if availability_selectors.is_on_time_off(staff.id, start_at, end_at):
        raise ValidationError("The staff member is unavailable (time off) then.")


def _enforce_client_limits(client, start_at, settings_row) -> None:
    day = start_at.astimezone(clinic_tz()).date()
    if (
        selectors.count_client_appointments_on_day(client.id, day)
        >= settings_row.max_appointments_per_day
    ):
        raise ValidationError(
            f"Daily limit reached ({settings_row.max_appointments_per_day} per day)."
        )
    if (
        selectors.count_client_appointments_in_week(client.id, day)
        >= settings_row.max_appointments_per_week
    ):
        raise ValidationError(
            f"Weekly limit reached ({settings_row.max_appointments_per_week} per week)."
        )


def _lock_staff(staff_id) -> None:
    """Serialize concurrent bookings for a staff member by locking their row.

    Postgres won't gap-lock a non-existent appointment, so we take a row lock on
    the staff member to make the availability re-check + insert atomic and
    prevent double-booking (see ddd.md concurrency rules).
    """
    get_user_model().objects.select_for_update().get(pk=staff_id)


# ------------------------------------------------------------
# Booking
# ------------------------------------------------------------

@transaction.atomic
def create_appointment(
    *,
    client,
    service,
    start_at,
    nail_art_option: str | None = None,
    batch: AppointmentBatch | None = None,
    notes: str = "",
    idempotency_key: str | None = None,
) -> Appointment:
    """Create a booked appointment with full server-side conflict checks.

    Auto-confirmed within the booking horizon (no staff approval). Idempotent on
    ``idempotency_key`` so retries/double-submits don't double-book.
    """
    now = timezone.now()
    settings_row = get_system_settings()

    if client.blacklisted:
        raise ValidationError(
            "This account can't book online. Please contact the studio directly."
        )
    if nail_art_option and not service.is_nail_service:
        raise ValidationError("This service does not support Nail Art.")

    duration = _compute_duration(client, service, nail_art_option)
    end_at = start_at + timedelta(minutes=duration)

    _validate_booking_window(start_at, settings_row, now)

    staff = service.staff
    _lock_staff(staff.id)

    if idempotency_key:
        existing = selectors.get_idempotent_appointment(idempotency_key)
        if existing is not None:
            return existing

    _validate_within_schedule(staff, start_at, end_at)
    _enforce_client_limits(client, start_at, settings_row)

    if selectors.has_overlapping_appointment(staff.id, start_at, end_at):
        raise ValidationError("That time was just taken — please pick another slot.")

    price, is_quote_only = _snapshot_price(service)

    appointment = Appointment.objects.create(
        batch=batch,
        client=client,
        staff=staff,
        service=service,
        status=AppointmentStatus.BOOKED,
        start_at=start_at,
        end_at=end_at,
        notes=notes,
        nail_art_option=nail_art_option,
        has_nail_art=bool(nail_art_option),
        price_snapshot=price,
        is_quote_only_snapshot=is_quote_only,
        duration_minutes_snapshot=duration,
        idempotency_key=idempotency_key,
    )

    from apps.notifications import services as notifications

    notifications.notify_appointment_confirmation(appointment=appointment)
    return appointment


@transaction.atomic
def create_batch(*, client, items: list[dict], idempotency_key: str | None = None):
    """Create an appointment batch (≤ ``max_appointments_per_batch``).

    Each appointment still passes the per-day/week limits and conflict checks.
    """
    settings_row = get_system_settings()
    if not items:
        raise ValidationError("A batch needs at least one appointment.")
    if len(items) > settings_row.max_appointments_per_batch:
        raise ValidationError(
            f"A batch can contain at most {settings_row.max_appointments_per_batch} appointments."
        )

    batch = AppointmentBatch.objects.create(client=client)
    created: list[Appointment] = []
    for index, item in enumerate(items):
        key = f"{idempotency_key}:{index}" if idempotency_key else None
        created.append(
            create_appointment(
                client=client,
                service=item["service"],
                start_at=item["start_at"],
                nail_art_option=item.get("nail_art_option"),
                batch=batch,
                notes=item.get("notes", ""),
                idempotency_key=key,
            )
        )
    return batch, created


# ------------------------------------------------------------
# Lifecycle
# ------------------------------------------------------------

@transaction.atomic
def cancel_appointment(*, appointment: Appointment, reason: str) -> Appointment:
    """Cancel an appointment, freeing the time and alerting the waitlist.

    ``reason=client`` self-cancellations are only allowed up to 24h before; closer
    than that the client must contact the staff member directly.
    """
    if appointment.status == AppointmentStatus.CANCELED:
        raise ValidationError("This appointment is already canceled.")
    if appointment.status in (AppointmentStatus.MADE, AppointmentStatus.NO_SHOW):
        raise ValidationError("A completed appointment cannot be canceled.")
    if reason == CancelReason.CLIENT and _within_cutoff(appointment.start_at):
        raise ValidationError(
            "Within 24h of the appointment — please contact the staff member directly."
        )

    appointment.status = AppointmentStatus.CANCELED
    appointment.cancel_reason = reason
    appointment.save(update_fields=["status", "cancel_reason", "updated_at"])

    _alert_waitlist(appointment)
    return appointment


@transaction.atomic
def reschedule_appointment(*, appointment: Appointment, new_start_at, by_client: bool) -> Appointment:
    """Move an appointment in place (status stays ``booked``; never a cancellation).

    Re-runs the availability checks at the new time and frees the old time for the
    waitlist. Self-service is blocked within 24h of the current start.
    """
    if appointment.status != AppointmentStatus.BOOKED:
        raise ValidationError("Only booked appointments can be rescheduled.")
    if by_client and _within_cutoff(appointment.start_at):
        raise ValidationError(
            "Within 24h of the appointment — please contact the staff member directly."
        )

    now = timezone.now()
    settings_row = get_system_settings()
    duration = appointment.duration_minutes_snapshot
    new_end = new_start_at + timedelta(minutes=duration)

    _validate_booking_window(new_start_at, settings_row, now)

    staff = appointment.staff
    _lock_staff(staff.id)
    _validate_within_schedule(staff, new_start_at, new_end)
    if selectors.has_overlapping_appointment(
        staff.id, new_start_at, new_end, exclude_id=appointment.id
    ):
        raise ValidationError("That time was just taken — please pick another slot.")

    freed_start_at = appointment.start_at
    appointment.start_at = new_start_at
    appointment.end_at = new_end
    appointment.save(update_fields=["start_at", "end_at", "updated_at"])

    # Alert the waitlist for the time that was just freed (the old start), not the new one.
    _alert_waitlist(appointment, at=freed_start_at)
    return appointment


@transaction.atomic
def mark_made(*, appointment: Appointment) -> Appointment:
    if appointment.status != AppointmentStatus.BOOKED:
        raise ValidationError("Only booked appointments can be marked as made.")
    appointment.status = AppointmentStatus.MADE
    appointment.save(update_fields=["status", "updated_at"])
    return appointment


@transaction.atomic
def mark_no_show(*, appointment: Appointment) -> Appointment:
    if appointment.status != AppointmentStatus.BOOKED:
        raise ValidationError("Only booked appointments can be marked as a no-show.")
    appointment.status = AppointmentStatus.NO_SHOW
    appointment.save(update_fields=["status", "updated_at"])
    return appointment


@transaction.atomic
def edit_nail_art(*, appointment: Appointment, nail_art_option: str | None) -> Appointment:
    """Change an appointment's Nail Art option. Staff-only (gated in the view).

    Clients are blocked from switching simple↔complex (a BO/staff-only change —
    see business-rules.md); the client app surfaces a "talk to staff" modal.
    """
    if not appointment.service.is_nail_service:
        raise ValidationError("This service does not support Nail Art.")
    if appointment.status != AppointmentStatus.BOOKED:
        raise ValidationError("Only booked appointments can be edited.")

    base = users_selectors.get_client_service_duration(
        appointment.client_id, appointment.service_id
    ) or appointment.service.duration_minutes
    if nail_art_option:
        base += NAIL_ART_EXTRA_MINUTES[NailArtOption(nail_art_option)]
    new_end = appointment.start_at + timedelta(minutes=base)

    staff = appointment.staff
    _lock_staff(staff.id)
    if selectors.has_overlapping_appointment(
        staff.id, appointment.start_at, new_end, exclude_id=appointment.id
    ):
        raise ValidationError("The new duration overlaps another appointment.")

    appointment.nail_art_option = nail_art_option
    appointment.has_nail_art = bool(nail_art_option)
    appointment.duration_minutes_snapshot = base
    appointment.end_at = new_end
    appointment.save(
        update_fields=[
            "nail_art_option",
            "has_nail_art",
            "duration_minutes_snapshot",
            "end_at",
            "updated_at",
        ]
    )
    return appointment


def _alert_waitlist(appointment: Appointment, *, at=None) -> None:
    from apps.notifications import services as notifications

    notifications.notify_waitlist_for_freed_time(
        staff_id=appointment.staff_id,
        service_id=appointment.service_id,
        start_at=at or appointment.start_at,
    )
