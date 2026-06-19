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
from .models import ClientServiceDuration, OtpCode, StaffEducation, User


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
# Client profile (self-service)
# ------------------------------------------------------------

# Fields a client may update about themselves. msisdn (login identifier) is not
# self-editable; role/blacklist are staff-controlled.
CLIENT_SELF_EDITABLE = {"first_name", "last_name", "email", "birthday", "preferred_channel"}


@transaction.atomic
def update_client_profile(*, client: User, **fields) -> User:
    """Update the calling client's own profile (restricted field set)."""
    disallowed = set(fields) - CLIENT_SELF_EDITABLE
    if disallowed:
        raise ValidationError(
            {field: "This field cannot be changed here." for field in disallowed}
        )
    for field, value in fields.items():
        setattr(client, field, value)
    client.full_clean(exclude=["password"])
    client.save()
    return client


# ------------------------------------------------------------
# Blacklist (staff-managed — see business-rules.md)
# ------------------------------------------------------------

@transaction.atomic
def set_blacklisted(*, client: User, blacklisted: bool) -> User:
    """Set/clear a client's blacklist flag. Only staff call this (gated in views)."""
    if client.role != UserRole.CLIENT:
        raise ValidationError("Only clients can be blacklisted.")
    client.blacklisted = blacklisted
    client.save(update_fields=["blacklisted", "updated_at"])
    return client


# ------------------------------------------------------------
# Per-client duration override
# ------------------------------------------------------------

@transaction.atomic
def set_client_service_duration(*, client: User, service, duration_minutes: int) -> ClientServiceDuration:
    if duration_minutes <= 0:
        raise ValidationError("Duration must be a positive number of minutes.")
    if client.role != UserRole.CLIENT:
        raise ValidationError("Duration overrides apply to clients only.")
    obj, _ = ClientServiceDuration.objects.update_or_create(
        client=client,
        service=service,
        defaults={"duration_minutes": duration_minutes},
    )
    return obj


@transaction.atomic
def clear_client_service_duration(*, client: User, service) -> None:
    ClientServiceDuration.objects.filter(client=client, service=service).delete()


# ------------------------------------------------------------
# Staff education (BO — see business-rules.md)
# ------------------------------------------------------------

@transaction.atomic
def create_staff_education(
    *,
    staff: User,
    education_type: str,
    provider: str,
    title: str,
    completed_on,
    description: str = "",
) -> StaffEducation:
    if staff.role != UserRole.STAFF:
        raise ValidationError("Education records belong to staff members.")
    education = StaffEducation(
        staff=staff,
        education_type=education_type,
        provider=provider,
        title=title,
        completed_on=completed_on,
        description=description,
    )
    education.full_clean()
    education.save()
    return education


@transaction.atomic
def update_staff_education(*, education: StaffEducation, **fields) -> StaffEducation:
    for field, value in fields.items():
        setattr(education, field, value)
    education.full_clean()
    education.save()
    return education


@transaction.atomic
def delete_staff_education(*, education: StaffEducation) -> None:
    education.delete()


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
