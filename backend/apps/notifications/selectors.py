from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from .models import BoAlert


def list_bo_alerts(staff_id: UUID, *, unread_only: bool = False) -> QuerySet[BoAlert]:
    qs = BoAlert.objects.filter(staff_id=staff_id)
    if unread_only:
        qs = qs.filter(is_read=False)
    return qs


def get_bo_alert(staff_id: UUID, alert_id: UUID) -> BoAlert | None:
    return BoAlert.objects.filter(pk=alert_id, staff_id=staff_id).first()
