"""Thin Twilio SMS client.

Invoked from app ``services.py`` / ``tasks.py`` (never from views — see
``backend.md``). When Twilio credentials are not configured (e.g. local dev),
the message is logged instead of sent, so flows like SMS OTP remain testable
without a real Twilio account.
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(
        settings.TWILIO_ACCOUNT_SID
        and settings.TWILIO_AUTH_TOKEN
        and settings.TWILIO_FROM_NUMBER
    )


def send_sms(to: str, body: str) -> None:
    """Send an SMS to ``to``.

    Raises on a real send failure so callers can surface a clear error; in the
    unconfigured (dev) case it logs the body and returns without raising.
    """
    if not is_configured():
        logger.warning("Twilio not configured — would send SMS to %s: %s", to, body)
        return

    # Imported lazily so the dependency is only needed when actually sending.
    from twilio.rest import Client

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(to=to, from_=settings.TWILIO_FROM_NUMBER, body=body)
    logger.info("Sent SMS to %s", to)
