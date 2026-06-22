"""Telnyx SMS client — fallback channel + login OTP transport.

Invoked from app ``services.py`` / ``tasks.py`` (never from views — see
``backend.md``). When credentials are not configured (e.g. local dev), the
message is logged instead of sent, so SMS OTP and the notification fallback
remain testable without a real Telnyx account. Replaces Twilio (see ADR 0007).
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(settings.TELNYX_API_KEY and settings.TELNYX_FROM_NUMBER)


def send_sms(to: str, body: str) -> None:
    """Send an SMS to ``to``.

    Raises on a real send failure so callers can surface a clear error (OTP) or
    fall back to another channel (notifications); in the unconfigured (dev) case
    it logs the body and returns without raising.
    """
    if not is_configured():
        logger.warning("Telnyx not configured — would send SMS to %s: %s", to, body)
        return

    # Imported lazily so the dependency is only needed when actually sending.
    import telnyx

    telnyx.api_key = settings.TELNYX_API_KEY
    telnyx.Message.create(from_=settings.TELNYX_FROM_NUMBER, to=to, text=body)
    logger.info("Sent SMS to %s", to)
