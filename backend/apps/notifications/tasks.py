"""Background & scheduled notification jobs (Procrastinate).

Task bodies contain no business logic — they delegate to the service layer and
are idempotent (sends are deduped via ``NotificationLog.dedup_key``). See
background-jobs.md.
"""

from datetime import timedelta

from django.utils import timezone
from procrastinate.contrib.django import app

from common.utils import clinic_tz


@app.task(name="notifications.send_appointment_confirmation", queue="notifications")
def send_appointment_confirmation(appointment_id: str) -> None:
    """Deferred booking confirmation (enqueued when an appointment is created)."""
    from apps.appointments import selectors as appt_selectors

    from . import services

    appointment = appt_selectors.get_appointment(appointment_id)
    if appointment is None:
        return
    services.send_appointment_confirmation_now(appointment=appointment)


@app.periodic(cron="0 9 * * *")
@app.task(name="notifications.send_due_reminders", queue="notifications")
def send_due_reminders(timestamp: int) -> None:
    """Daily: remind clients of appointments happening the next local day (~24h)."""
    from apps.appointments import selectors as appt_selectors

    from . import services

    tomorrow = (timezone.now().astimezone(clinic_tz()) + timedelta(days=1)).date()
    for appointment in appt_selectors.list_booked_appointments_on_local_date(tomorrow):
        services.send_appointment_reminder_now(appointment=appointment)


@app.periodic(cron="0 10 * * *")
@app.task(name="notifications.send_birthday_messages", queue="notifications")
def send_birthday_messages(timestamp: int) -> None:
    """Daily: wish clients a happy birthday on behalf of the studio."""
    from apps.users import selectors as users_selectors

    from . import services

    today = timezone.now().astimezone(clinic_tz()).date()
    for client in users_selectors.list_clients_with_birthday(today.month, today.day):
        services.send_birthday_message_now(client=client, year=today.year)
