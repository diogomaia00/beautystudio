from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from .models import MonthlyReport


def list_reports(staff_id: UUID) -> QuerySet[MonthlyReport]:
    return MonthlyReport.objects.filter(staff_id=staff_id)


def get_report(report_id: UUID) -> MonthlyReport | None:
    return MonthlyReport.objects.select_related("staff").filter(pk=report_id).first()


def get_report_for_period(staff_id: UUID, year: int, month: int) -> MonthlyReport | None:
    return MonthlyReport.objects.filter(staff_id=staff_id, year=year, month=month).first()
