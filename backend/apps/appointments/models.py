import uuid

from django.conf import settings
from django.db import models

from common.constants import AppointmentStatus, CancelReason, NailArtOption


class AppointmentBatch(models.Model):
    """A group of appointments a client books together (max size in settings)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointment_batches",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "appointments_batch"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"batch {self.id}"


class Appointment(models.Model):
    """A single booking, stored as a UTC ``start_at``/``end_at`` range.

    Price and duration are **snapshotted** at booking time (see ADR 0001) so later
    BO price edits never rewrite historical revenue. A reschedule updates the
    range in place (status stays ``booked``); only a genuine cancellation sets
    ``status = canceled`` with a ``cancel_reason``.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(
        AppointmentBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="staff_appointments",
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    status = models.CharField(
        max_length=20, choices=AppointmentStatus.choices, default=AppointmentStatus.BOOKED
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    notes = models.TextField(blank=True)

    # Nail Art add-on (clients book it but cannot switch simple↔complex; staff-only edit).
    nail_art_option = models.CharField(
        max_length=10, choices=NailArtOption.choices, null=True, blank=True
    )
    has_nail_art = models.BooleanField(default=False)

    # Snapshots taken at booking time.
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_quote_only_snapshot = models.BooleanField(default=False)
    duration_minutes_snapshot = models.PositiveIntegerField()

    cancel_reason = models.CharField(
        max_length=20, choices=CancelReason.choices, null=True, blank=True
    )
    # Idempotency for concurrent/double-submitted bookings (see ddd.md).
    idempotency_key = models.CharField(max_length=64, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "appointments_appointment"
        ordering = ["start_at"]
        constraints = [
            models.CheckConstraint(
                name="appointment_range_valid",
                check=models.Q(end_at__gt=models.F("start_at")),
            ),
            models.UniqueConstraint(
                fields=["idempotency_key"],
                condition=models.Q(idempotency_key__isnull=False),
                name="uniq_appointment_idempotency_key",
            ),
        ]
        indexes = [
            models.Index(fields=["staff", "start_at"], name="appointment_staff_start_idx"),
            models.Index(fields=["client", "start_at"], name="appointment_client_start_idx"),
            models.Index(fields=["status", "start_at"], name="appointment_status_start_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.service_id} @ {self.start_at} ({self.status})"
