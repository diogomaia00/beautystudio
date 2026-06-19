from __future__ import annotations

from collections import Counter
from decimal import Decimal
from uuid import UUID

from apps.appointments import selectors as appt_selectors
from common.constants import AppointmentStatus


def compute_staff_monthly_metrics(staff_id: UUID, year: int, month: int) -> dict:
    """Aggregate a staff member's metrics for a local calendar month.

    Reads appointments through the ``appointments`` selector layer (anti-corruption
    boundary — see ddd.md) and computes the figures the monthly report needs:
    hours worked, appointment counts by status, distinct/new clients, top-3
    services, revenue (total and per service), and revenue per hour worked.

    Revenue uses the **price snapshot** taken at booking time (ADR 0001); quote-only
    appointments contribute no revenue. Only ``made`` appointments count as worked.
    """
    appointments = list(appt_selectors.list_staff_appointments_in_local_month(staff_id, year, month))
    month_start, _ = appt_selectors.local_month_bounds(year, month)

    made = [a for a in appointments if a.status == AppointmentStatus.MADE]

    counts = {
        "booked": sum(1 for a in appointments if a.status == AppointmentStatus.BOOKED),
        "made": len(made),
        "canceled": sum(1 for a in appointments if a.status == AppointmentStatus.CANCELED),
        "no_show": sum(1 for a in appointments if a.status == AppointmentStatus.NO_SHOW),
    }

    minutes_worked = sum(a.duration_minutes_snapshot for a in made)
    hours_worked = round(minutes_worked / 60, 2)

    distinct_clients = {a.client_id for a in made}
    returning = appt_selectors.client_ids_with_made_before(staff_id, month_start)
    new_clients = distinct_clients - returning

    service_counts: Counter = Counter(a.service.name for a in made)
    top_services = [
        {"service": name, "count": count}
        for name, count in service_counts.most_common(3)
    ]

    revenue_total = Decimal("0.00")
    revenue_by_service: dict[str, Decimal] = {}
    for a in made:
        if a.is_quote_only_snapshot or a.price_snapshot is None:
            continue
        revenue_total += a.price_snapshot
        revenue_by_service[a.service.name] = (
            revenue_by_service.get(a.service.name, Decimal("0.00")) + a.price_snapshot
        )

    revenue_per_hour = (
        float(round(revenue_total / Decimal(str(hours_worked)), 2)) if hours_worked else 0.0
    )

    return {
        "staff_id": str(staff_id),
        "year": year,
        "month": month,
        "hours_worked": hours_worked,
        "appointments": counts,
        "distinct_clients": len(distinct_clients),
        "new_clients": len(new_clients),
        "top_services": top_services,
        "revenue_total": str(revenue_total),
        "revenue_by_service": {k: str(v) for k, v in revenue_by_service.items()},
        "revenue_per_hour": revenue_per_hour,
    }
