from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, transaction

from common.constants import BoAlertType, NotificationChannel
from common.utils import clinic_tz
from integrations.twilio.client import send_sms

from .models import BoAlert, NotificationLog, NotificationStatus

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Client notifications (respect the preferred channel)
# ------------------------------------------------------------

def _deliver(*, client, subject: str, body: str) -> str:
    """Send via the client's preferred channel; return the resulting status."""
    channel = client.preferred_channel or NotificationChannel.SMS
    try:
        if channel == NotificationChannel.EMAIL:
            if not client.email:
                return NotificationStatus.SKIPPED
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [client.email])
        else:
            send_sms(client.msisdn, body)
    except Exception:  # noqa: BLE001 — log and mark failed; never crash the caller
        logger.exception("Notification delivery failed for %s", client.id)
        return NotificationStatus.FAILED
    return NotificationStatus.SENT


def send_to_client(*, client, subject: str, body: str, dedup_key: str | None = None) -> NotificationLog | None:
    """Send a notification to a client, deduplicated by ``dedup_key`` if given.

    Returns ``None`` when the message was already sent (idempotent) — safe for
    retried periodic tasks (see background-jobs.md).
    """
    channel = client.preferred_channel or NotificationChannel.SMS
    if dedup_key and NotificationLog.objects.filter(dedup_key=dedup_key).exists():
        return None

    status = _deliver(client=client, subject=subject, body=body)
    try:
        with transaction.atomic():
            return NotificationLog.objects.create(
                recipient=client,
                channel=channel,
                subject=subject,
                body=body,
                status=status,
                dedup_key=dedup_key,
            )
    except IntegrityError:
        # A concurrent task already logged this dedup_key — treat as already sent.
        return None


def _format_appointment_line(appointment) -> str:
    local = appointment.start_at.astimezone(clinic_tz())
    when = local.strftime("%d/%m/%Y %H:%M")
    price = (
        "sob consulta"
        if appointment.is_quote_only_snapshot or appointment.price_snapshot is None
        else f"{appointment.price_snapshot}€"
    )
    return f"{appointment.service.name} — {when} ({price})"


def send_appointment_confirmation_now(*, appointment) -> None:
    body = (
        "A tua marcação Beauty Studio está confirmada:\n"
        f"{_format_appointment_line(appointment)}"
    )
    send_to_client(
        client=appointment.client,
        subject="Marcação confirmada — Beauty Studio",
        body=body,
        dedup_key=f"confirmation:{appointment.id}",
    )


def send_appointment_reminder_now(*, appointment) -> None:
    body = (
        "Lembrete Beauty Studio — tens uma marcação amanhã:\n"
        f"{_format_appointment_line(appointment)}"
    )
    send_to_client(
        client=appointment.client,
        subject="Lembrete de marcação — Beauty Studio",
        body=body,
        dedup_key=f"reminder:{appointment.id}",
    )


def send_birthday_message_now(*, client, year: int) -> None:
    send_to_client(
        client=client,
        subject="Parabéns! — Beauty Studio",
        body="A equipa Beauty Studio deseja-te um feliz aniversário! 🎉",
        dedup_key=f"birthday:{client.id}:{year}",
    )


# ------------------------------------------------------------
# Confirmation enqueue (deferred — event driven)
# ------------------------------------------------------------

def notify_appointment_confirmation(*, appointment) -> None:
    """Enqueue the booking confirmation send (runs on the worker)."""
    from . import tasks

    tasks.send_appointment_confirmation.defer(appointment_id=str(appointment.id))


# ------------------------------------------------------------
# Back-office alerts (in-app)
# ------------------------------------------------------------

def create_bo_alert(*, staff, alert_type: str, title: str, body: str = "") -> BoAlert:
    return BoAlert.objects.create(
        staff=staff, alert_type=alert_type, title=title, body=body
    )


def notify_staff_waitlist_join(*, waitlist) -> BoAlert:
    local = waitlist.desired_start_at.astimezone(clinic_tz()).strftime("%d/%m/%Y %H:%M")
    return create_bo_alert(
        staff=waitlist.staff,
        alert_type=BoAlertType.WAITLIST_JOIN,
        title="Nova entrada na lista de espera",
        body=f"{waitlist.client.msisdn} aguarda por {waitlist.service.name} em {local}.",
    )


def notify_staff_custom_request(*, custom_request) -> BoAlert:
    return create_bo_alert(
        staff=custom_request.staff,
        alert_type=BoAlertType.CUSTOM_REQUEST,
        title="Novo pedido de marcação personalizado",
        body=(
            f"{custom_request.client.msisdn} pediu {custom_request.service.name} "
            f"em {custom_request.preferred_date}."
        ),
    )


def notify_waitlist_for_freed_time(*, staff_id, service_id, start_at) -> BoAlert | None:
    """Alert the staff member that a booked time was freed and someone is waiting."""
    from apps.availability import selectors as availability_selectors
    from apps.users import selectors as users_selectors

    waiting = list(availability_selectors.list_waitlist_for_time(staff_id, start_at))
    if not waiting:
        return None
    staff = users_selectors.get_user_by_id(staff_id)
    local = start_at.astimezone(clinic_tz()).strftime("%d/%m/%Y %H:%M")
    return create_bo_alert(
        staff=staff,
        alert_type=BoAlertType.WAITLIST_JOIN,
        title="Horário libertado com lista de espera",
        body=f"{len(waiting)} cliente(s) em espera para {local}.",
    )


def mark_alert_read(*, alert: BoAlert) -> BoAlert:
    alert.is_read = True
    alert.save(update_fields=["is_read"])
    return alert
