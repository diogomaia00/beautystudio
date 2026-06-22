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
    WHATSAPP = "whatsapp", "WhatsApp"
    SMS = "sms", "SMS"
    EMAIL = "email", "Email"


# Default delivery cascade for client notifications: WhatsApp first, SMS
# fallback, email complementary (see ADR 0007). A client's preferred_channel,
# when set, is tried before the rest of this order.
NOTIFICATION_CHANNEL_PRIORITY = [
    NotificationChannel.WHATSAPP,
    NotificationChannel.SMS,
    NotificationChannel.EMAIL,
]


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


class EducationType(models.TextChoices):
    FORMATION = "formation", "Formation"
    WEBINAR = "webinar", "Webinar"
    COURSE = "course", "Course"
    WORKSHOP = "workshop", "Workshop"
    OTHER = "other", "Other"


class WaitlistStatus(models.TextChoices):
    WAITING = "waiting", "Waiting"
    CONTACTED = "contacted", "Contacted"
    CLOSED = "closed", "Closed"


class CustomRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    CLOSED = "closed", "Closed"


class BoAlertType(models.TextChoices):
    WAITLIST_JOIN = "waitlist_join", "Waitlist join"
    CUSTOM_REQUEST = "custom_request", "Custom booking request"


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

# Minimum age (in years) required to create a client account (see business-rules.md).
MIN_SIGNUP_AGE_YEARS = 12
