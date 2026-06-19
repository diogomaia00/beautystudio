import uuid

from django.conf import settings
from django.db import models


class MonthlyReport(models.Model):
    """A generated monthly report for a staff member, shown in the BO.

    The computed figures are stored as JSON (``metrics``) so a report reflects the
    data at generation time and is cheap to read. Regenerating overwrites the row
    for that (staff, year, month).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="monthly_reports",
    )
    year = models.PositiveIntegerField()
    month = models.PositiveSmallIntegerField()
    metrics = models.JSONField()
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reports_monthly_report"
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(
                fields=["staff", "year", "month"], name="uniq_monthly_report_period"
            ),
            models.CheckConstraint(
                name="monthly_report_month_range",
                check=models.Q(month__gte=1) & models.Q(month__lte=12),
            ),
        ]

    def __str__(self) -> str:
        return f"report {self.staff_id} {self.year}-{self.month:02d}"
