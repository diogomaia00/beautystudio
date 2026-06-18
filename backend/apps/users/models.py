import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from common.constants import NotificationChannel, UserRole


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.CLIENT)
    msisdn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    preferred_channel = models.CharField(
        max_length=10,
        choices=NotificationChannel.choices,
        default=NotificationChannel.SMS,
    )
    blacklisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "msisdn"
    REQUIRED_FIELDS = ["username", "email"]

    class Meta:
        db_table = "users_user"
