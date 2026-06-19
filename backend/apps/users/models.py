import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

from common.constants import NotificationChannel, OtpPurpose, UserRole


class UserManager(BaseUserManager):
    """Manager for the msisdn-identified custom user.

    The default ``UserManager`` keys on ``username``; this app authenticates by
    ``msisdn`` (SMS OTP — see ADR 0004), so user creation keys on it instead.
    App users have no usable password (OTP only); the admin superuser keeps a
    password for Django ``/admin/``.
    """

    use_in_migrations = True

    def _create_user(self, msisdn, password=None, **extra_fields):
        if not msisdn:
            raise ValueError("Users must have an msisdn")
        user = self.model(msisdn=msisdn, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, msisdn, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(msisdn, password, **extra_fields)

    def create_superuser(self, msisdn, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self._create_user(msisdn, password, **extra_fields)


class User(AbstractUser):
    # Login is by msisdn (SMS OTP), so the inherited username field is dropped.
    username = None

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.CLIENT)
    msisdn = models.CharField(max_length=20, unique=True)
    birthday = models.DateField(null=True, blank=True)
    preferred_channel = models.CharField(
        max_length=10,
        choices=NotificationChannel.choices,
        default=NotificationChannel.SMS,
    )
    blacklisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "msisdn"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "users_user"

    def __str__(self) -> str:
        return self.msisdn


class OtpCode(models.Model):
    """A single-use SMS one-time code (see auth.md / ADR 0004).

    Only the **hash** of the code is stored, never the plaintext. For ``login``
    the code is tied to a ``user``; for ``signup`` the user does not exist yet,
    so it is tied to ``msisdn`` only (``user`` is NULL) and resolved on verify.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="otp_codes",
    )
    msisdn = models.CharField(max_length=20)
    code_hash = models.CharField(max_length=128)
    purpose = models.CharField(
        max_length=20,
        choices=OtpPurpose.choices,
        default=OtpPurpose.LOGIN,
    )
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "otp_code"
        indexes = [
            models.Index(fields=["user", "expires_at"], name="otp_user_expires_idx"),
            models.Index(fields=["msisdn", "expires_at"], name="otp_msisdn_expires_idx"),
        ]

    def __str__(self) -> str:
        return f"OTP {self.purpose} for {self.msisdn}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_consumed(self) -> bool:
        return self.consumed_at is not None
