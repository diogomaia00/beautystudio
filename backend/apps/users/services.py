import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, Throttled, ValidationError

from common.constants import (
    OTP_CODE_LENGTH,
    OTP_CODE_TTL_MINUTES,
    OTP_MAX_REQUESTS_PER_HOUR,
    OTP_MAX_VERIFY_ATTEMPTS,
    OTP_REQUEST_COOLDOWN_SECONDS,
    OtpPurpose,
    UserRole,
)
from integrations.twilio.client import send_sms

from . import selectors
from .models import OtpCode, User


# ------------------------------------------------------------
# OTP helpers
# ------------------------------------------------------------

def _generate_code() -> str:
    """Return a zero-padded numeric one-time code."""
    return f"{secrets.randbelow(10 ** OTP_CODE_LENGTH):0{OTP_CODE_LENGTH}d}"


def _hash_code(msisdn: str, code: str) -> str:
    """HMAC-SHA256 of the code, salted with the msisdn and the server secret.

    Deterministic so verify is a constant-time compare; the plaintext code is
    never stored (see ADR 0004).
    """
    message = f"{msisdn}:{code}".encode()
    return hmac.new(settings.SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()


def _enforce_request_rate_limit(msisdn: str, now) -> None:
    window_start = now - timedelta(hours=1)
    recent = OtpCode.objects.filter(msisdn=msisdn, created_at__gte=window_start)
    if recent.count() >= OTP_MAX_REQUESTS_PER_HOUR:
        raise Throttled(detail="Too many code requests. Please try again later.")
    last = recent.order_by("-created_at").first()
    if last is not None:
        elapsed = (now - last.created_at).total_seconds()
        if elapsed < OTP_REQUEST_COOLDOWN_SECONDS:
            wait = int(OTP_REQUEST_COOLDOWN_SECONDS - elapsed)
            raise Throttled(wait=wait, detail="A code was just sent. Please wait.")


# ------------------------------------------------------------
# Account creation
# ------------------------------------------------------------

@transaction.atomic
def create_client(*, msisdn: str, **profile_fields) -> User:
    """Create an active client account identified by ``msisdn`` (OTP-only)."""
    return User.objects.create_user(
        msisdn=msisdn,
        role=UserRole.CLIENT,
        is_active=True,
        **profile_fields,
    )


# ------------------------------------------------------------
# OTP flow (request → verify → session)
# ------------------------------------------------------------

@transaction.atomic
def request_otp(*, msisdn: str, purpose: str) -> OtpCode:
    """Issue and send a one-time code to ``msisdn`` for ``login`` or ``signup``.

    Enforces per-msisdn rate limiting and the account-existence rules for each
    purpose. The plaintext code is sent via SMS and never returned.
    """
    now = timezone.now()
    _enforce_request_rate_limit(msisdn, now)

    user = selectors.get_user_by_msisdn(msisdn)
    if purpose == OtpPurpose.LOGIN:
        if user is None:
            raise ValidationError("No account exists for this number. Please sign up.")
        if not user.is_active:
            raise PermissionDenied("This account is disabled. Contact the studio.")
    elif purpose == OtpPurpose.SIGNUP:
        if user is not None:
            raise ValidationError("An account already exists for this number. Please log in.")

    code = _generate_code()
    otp = OtpCode.objects.create(
        user=user if purpose == OtpPurpose.LOGIN else None,
        msisdn=msisdn,
        code_hash=_hash_code(msisdn, code),
        purpose=purpose,
        expires_at=now + timedelta(minutes=OTP_CODE_TTL_MINUTES),
    )

    send_sms(
        msisdn,
        f"O seu código Beauty Studio é {code}. Expira em {OTP_CODE_TTL_MINUTES} minutos.",
    )
    return otp


def verify_otp(*, msisdn: str, code: str, purpose: str, signup_data: dict | None = None) -> User:
    """Verify a one-time code and return the authenticated/created user.

    The view is responsible for establishing the Django session on the returned
    user. Codes are single-use, short-TTL, and attempt-capped.
    """
    # A wrong-code attempt must be persisted even though it ends in an error, so
    # the attempt counter survives. We therefore commit inside the locked block
    # and raise the deferred error only after the transaction has committed.
    invalid_code = False
    with transaction.atomic():
        otp = (
            OtpCode.objects.select_for_update()
            .filter(msisdn=msisdn, purpose=purpose, consumed_at__isnull=True)
            .order_by("-created_at")
            .first()
        )
        if otp is None:
            raise ValidationError("No active code. Please request a new one.")
        if otp.is_expired:
            raise ValidationError("This code has expired. Please request a new one.")
        if otp.attempts >= OTP_MAX_VERIFY_ATTEMPTS:
            raise Throttled(detail="Too many attempts. Please request a new code.")

        otp.attempts += 1
        if not hmac.compare_digest(otp.code_hash, _hash_code(msisdn, code)):
            otp.save(update_fields=["attempts", "updated_at"])
            invalid_code = True
        else:
            otp.consumed_at = timezone.now()
            otp.save(update_fields=["attempts", "consumed_at", "updated_at"])

    if invalid_code:
        raise ValidationError("Invalid code.")

    if purpose == OtpPurpose.LOGIN:
        user = otp.user or selectors.get_user_by_msisdn(msisdn)
        if user is None or not user.is_active:
            raise PermissionDenied("This account is unavailable.")
        return user

    # signup: the number is now verified — create the account.
    if selectors.get_user_by_msisdn(msisdn) is not None:
        raise ValidationError("An account already exists for this number.")
    return create_client(msisdn=msisdn, **(signup_data or {}))
