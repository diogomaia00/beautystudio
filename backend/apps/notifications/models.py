import uuid

from django.conf import settings
from django.db import models

from common.constants import BoAlertType, NotificationChannel


class NotificationStatus(models.TextChoices):
    SENT = "sent", "Sent"
    SKIPPED = "skipped", "Skipped"
    FAILED = "failed", "Failed"


class NotificationLog(models.Model):
    """A record of an outbound client notification (email/SMS).

    ``dedup_key`` makes idempotent sends possible (a periodic reminder/birthday
    task can be retried without double-sending — see background-jobs.md).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=NotificationStatus.choices)
    dedup_key = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications_log"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["dedup_key"],
                condition=models.Q(dedup_key__isnull=False),
                name="uniq_notification_dedup_key",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.channel} -> {self.recipient_id} ({self.status})"


class BoAlert(models.Model):
    """An in-app back-office alert for a staff member.

    Event-driven (waitlist joins, custom booking requests) — staff act on these
    in the BO; there is no automatic offer/booking in v1 (business-rules.md).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bo_alerts",
    )
    alert_type = models.CharField(max_length=20, choices=BoAlertType.choices)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications_bo_alert"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["staff", "is_read"], name="bo_alert_staff_read_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.alert_type} for {self.staff_id}"
