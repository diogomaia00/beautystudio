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
