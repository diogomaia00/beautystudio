from django.db import models


class SystemSettings(models.Model):
    """Single-clinic scheduling configuration (a singleton row).

    Lives in the DB so staff/admin can tune booking behaviour from the back
    office without a deploy. Enforced as a single row (pk is always 1).
    Recommended defaults mirror ``database.md``.
    """

    booking_slot_minutes = models.PositiveIntegerField(default=15)
    booking_horizon_days = models.PositiveIntegerField(default=60)
    minimum_notice_hours = models.PositiveIntegerField(default=2)
    max_appointments_per_day = models.PositiveIntegerField(default=3)
    max_appointments_per_week = models.PositiveIntegerField(default=3)
    max_appointments_per_batch = models.PositiveIntegerField(default=3)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_settings"
        verbose_name = "System settings"
        verbose_name_plural = "System settings"

    def __str__(self) -> str:
        return "System settings"

    def save(self, *args, **kwargs):
        # Force the singleton: there is only ever one row.
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # The singleton is never deleted.
        return 0, {}
