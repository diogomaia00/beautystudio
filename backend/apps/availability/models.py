import uuid

from django.conf import settings
from django.db import models

from common.constants import CustomRequestStatus, WaitlistStatus


class StaffSchedule(models.Model):
    """A recurring weekly working window for a staff member.

    ``weekday`` uses the clinic encoding ``1=Sun … 7=Sat`` (see database.md);
    always map dates through ``common.utils.clinic_weekday``.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    weekday = models.PositiveSmallIntegerField()  # 1=Sun … 7=Sat
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "staff_schedules"
        ordering = ["weekday", "start_time"]
        constraints = [
            models.CheckConstraint(
                name="schedule_weekday_range",
                check=models.Q(weekday__gte=1) & models.Q(weekday__lte=7),
            ),
            models.CheckConstraint(
                name="schedule_window_valid",
                check=models.Q(end_time__gt=models.F("start_time")),
            ),
        ]
        indexes = [
            models.Index(fields=["staff", "weekday"], name="schedule_staff_weekday_idx"),
        ]

    def __str__(self) -> str:
        return f"staff={self.staff_id} wd={self.weekday} {self.start_time}-{self.end_time}"


class StaffBreak(models.Model):
    """A recurring non-bookable daily window (e.g. lunch) for a staff member."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="breaks",
    )
    weekday = models.PositiveSmallIntegerField()  # 1=Sun … 7=Sat
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "staff_breaks"
        ordering = ["weekday", "start_time"]
        constraints = [
            models.CheckConstraint(
                name="break_weekday_range",
                check=models.Q(weekday__gte=1) & models.Q(weekday__lte=7),
            ),
            models.CheckConstraint(
                name="break_window_valid",
                check=models.Q(end_time__gt=models.F("start_time")),
            ),
        ]
        indexes = [
            models.Index(fields=["staff", "weekday"], name="break_staff_weekday_idx"),
        ]

    def __str__(self) -> str:
        return f"break staff={self.staff_id} wd={self.weekday}"


class StaffTimeOff(models.Model):
    """A one-off unavailable period (vacation, sick leave, holiday) in UTC."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="time_off",
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "staff_time_off"
        ordering = ["-start_at"]
        constraints = [
            models.CheckConstraint(
                name="time_off_window_valid",
                check=models.Q(end_at__gt=models.F("start_at")),
            ),
        ]
        indexes = [
            models.Index(fields=["staff", "start_at", "end_at"], name="time_off_staff_range_idx"),
        ]

    def __str__(self) -> str:
        return f"time off staff={self.staff_id} {self.start_at}–{self.end_at}"


class Waitlist(models.Model):
    """A client waiting on an occupied time (see business-rules.md).

    Joining notifies the responsible staff member in the BO; no automatic offer
    in v1 — staff contact the client outside the app.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="waitlist_entries",
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="waitlist_for_staff",
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="waitlist_entries",
    )
    desired_start_at = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=WaitlistStatus.choices, default=WaitlistStatus.WAITING
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "availability_waitlist"
        ordering = ["desired_start_at", "created_at"]
        indexes = [
            models.Index(fields=["staff", "status"], name="waitlist_staff_status_idx"),
            models.Index(fields=["desired_start_at"], name="waitlist_desired_idx"),
        ]

    def __str__(self) -> str:
        return f"waitlist {self.client_id} -> {self.desired_start_at}"


class CustomBookingRequest(models.Model):
    """A request to book beyond the booking horizon (see business-rules.md).

    Not auto-confirmed: the responsible staff member handles it in the BO.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="custom_requests",
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="custom_requests_for_staff",
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="custom_requests",
    )
    preferred_date = models.DateField()
    preferred_time = models.TimeField(null=True, blank=True)
    note = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=CustomRequestStatus.choices, default=CustomRequestStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "availability_custom_request"
        ordering = ["preferred_date", "created_at"]
        indexes = [
            models.Index(fields=["staff", "status"], name="custom_req_staff_status_idx"),
        ]

    def __str__(self) -> str:
        return f"custom request {self.client_id} -> {self.preferred_date}"
