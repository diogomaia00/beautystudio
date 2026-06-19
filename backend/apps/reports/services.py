from __future__ import annotations

from django.db import transaction

from apps.analytics import selectors as analytics_selectors

from .models import MonthlyReport


@transaction.atomic
def generate_monthly_report(*, staff, year: int, month: int) -> MonthlyReport:
    """Compute and persist a staff member's monthly report (idempotent upsert).

    Delegates the figures to the ``analytics`` layer and stores the snapshot for
    the BO to read (see background-jobs.md).
    """
    metrics = analytics_selectors.compute_staff_monthly_metrics(staff.id, year, month)
    report, _ = MonthlyReport.objects.update_or_create(
        staff=staff,
        year=year,
        month=month,
        defaults={"metrics": metrics},
    )
    return report
