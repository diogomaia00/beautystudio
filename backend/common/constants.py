from django.db import models

# ------------------------------------------------------------
# ENUM = "DB value", "Display value"
# ------------------------------------------------------------

class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    STAFF = "staff", "Staff"
    CLIENT = "client", "Client"


class AppointmentStatus(models.TextChoices):
    BOOKED = "booked", "Booked"
    MADE = "made", "Made"
    CANCELED = "canceled", "Canceled"
    NO_SHOW = "no_show", "No Show"


class NotificationChannel(models.TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"


class CancelReason(models.TextChoices):
    CLIENT = "client", "Client"
    STAFF = "staff", "Staff"


class NailArtOption(models.TextChoices):
    SIMPLE = "simple", "Simple"
    COMPLEX = "complex", "Complex"


NAIL_ART_EXTRA_MINUTES = {
    NailArtOption.SIMPLE: 15,
    NailArtOption.COMPLEX: 30,
}


class OtpPurpose(models.TextChoices):
    LOGIN = "login", "Login"
    SIGNUP = "signup", "Signup"


# ------------------------------------------------------------
# SMS OTP login (see auth.md / ADR 0004)
# ------------------------------------------------------------

# Number of digits in a one-time code.
OTP_CODE_LENGTH = 6
# How long a code stays valid after it is issued.
OTP_CODE_TTL_MINUTES = 5
# Max verify attempts against a single code before it is locked out.
OTP_MAX_VERIFY_ATTEMPTS = 5
# Min seconds between two code requests for the same msisdn (anti SMS-bombing).
OTP_REQUEST_COOLDOWN_SECONDS = 60
# Max code requests per msisdn within a rolling hour.
OTP_MAX_REQUESTS_PER_HOUR = 5
