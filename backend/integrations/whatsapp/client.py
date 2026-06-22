"""WhatsApp Cloud API (Meta) client — primary notification channel.

Invoked from app ``services.py`` / ``tasks.py`` (never from views — see
``backend.md``). When credentials are not configured (e.g. local dev), the
message is logged instead of sent, so notification flows remain testable without
a real Meta account.

> Business-initiated messages (reminders, birthday, campaigns) require a
> **pre-approved template** in Meta Business Manager — free-form text is only
> allowed inside a 24h customer-service window. The ``template`` argument names
> that template; the real implementation will POST to the Graph API
> (``/{phone_number_id}/messages``). See ADR 0007.
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppError(Exception):
    """Raised on a real WhatsApp send failure so callers can fall back to SMS."""


def is_configured() -> bool:
    return bool(
        settings.WHATSAPP_PHONE_NUMBER_ID and settings.WHATSAPP_ACCESS_TOKEN
    )


def send_whatsapp(to: str, body: str, *, template: str | None = None) -> None:
    """Send a WhatsApp message to ``to`` (E.164).

    Raises ``WhatsAppError`` on a real send failure; in the unconfigured (dev)
    case it logs the body and returns without raising.
    """
    if not is_configured():
        logger.warning(
            "WhatsApp not configured — would send to %s (template=%s): %s",
            to,
            template,
            body,
        )
        return

    # TODO(real wiring): POST https://graph.facebook.com/<version>/<phone_number_id>/messages
    # with a template payload. Until then, treat as not yet implemented so the
    # caller falls back to SMS rather than silently dropping the message.
    raise WhatsAppError("WhatsApp Cloud API send is not implemented yet.")
