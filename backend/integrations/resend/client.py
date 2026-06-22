"""Resend email client — complementary notification channel.

Invoked from app ``services.py`` / ``tasks.py`` (never from views — see
``backend.md``). When ``RESEND_API_KEY`` is not configured (e.g. local dev), it
falls back to Django's email backend (the console backend in dev), so email
flows remain testable without a real Resend account. See ADR 0007.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(settings.RESEND_API_KEY)


def send_email(to: str, subject: str, body: str) -> None:
    """Send an email to ``to``.

    Raises on a real send failure so callers can mark the notification failed;
    in the unconfigured (dev) case it uses Django's email backend (console).
    """
    if not is_configured():
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to])
        return

    # Imported lazily so the dependency is only needed when actually sending.
    import resend

    resend.api_key = settings.RESEND_API_KEY
    resend.Emails.send(
        {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [to],
            "subject": subject,
            "text": body,
        }
    )
    logger.info("Sent email to %s", to)
