"""Scheduled report jobs (Procrastinate).

Task bodies contain no business logic — they delegate to the service layer and
are idempotent (the report upsert overwrites the period's row). See
background-jobs.md.
"""

from datetime import timedelta

from django.utils import timezone
from procrastinate.contrib.django import app

from common.utils import clinic_tz


@app.periodic(cron="0 2 1 * *")
@app.task(name="reports.generate_previous_month_reports", queue="reports")
def generate_previous_month_reports(timestamp: int) -> None:
    """On the first of each month, generate every staff member's previous-month report."""
    from apps.users import selectors as users_selectors

    from . import services

    today = timezone.now().astimezone(clinic_tz()).date()
    last_month_day = today.replace(day=1) - timedelta(days=1)
    year, month = last_month_day.year, last_month_day.month

    for staff in users_selectors.list_staff():
        services.generate_monthly_report(staff=staff, year=year, month=month)
