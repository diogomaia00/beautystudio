from __future__ import annotations

from typing import Optional
from uuid import UUID

from django.db.models import QuerySet
from django.utils import timezone

from .models import Service, ServiceCategory, ServiceDiscount


def list_categories() -> QuerySet[ServiceCategory]:
    """All service categories, ordered for display."""
    return ServiceCategory.objects.all()


def get_category(category_id: UUID) -> Optional[ServiceCategory]:
    return ServiceCategory.objects.filter(pk=category_id).first()


def get_service(service_id: UUID) -> Optional[Service]:
    """A single service with its category and staff prefetched."""
    return (
        Service.objects.select_related("category", "staff")
        .filter(pk=service_id)
        .first()
    )


def list_services(
    *,
    category_id: UUID | None = None,
    staff_id: UUID | None = None,
    active_only: bool = True,
) -> QuerySet[Service]:
    """Catalog query with optional category/staff filters (no N+1)."""
    qs = Service.objects.select_related("category", "staff")
    if active_only:
        qs = qs.filter(is_active=True)
    if category_id is not None:
        qs = qs.filter(category_id=category_id)
    if staff_id is not None:
        qs = qs.filter(staff_id=staff_id)
    return qs


def get_active_discount(service: Service, at=None) -> Optional[ServiceDiscount]:
    """Return the active discount covering ``at`` (default now), or ``None``.

    If several overlap, the one with the highest percentage wins (best price for
    the client).
    """
    at = at or timezone.now()
    return (
        ServiceDiscount.objects.filter(
            service=service,
            is_active=True,
            starts_at__lte=at,
            ends_at__gt=at,
        )
        .order_by("-percentage")
        .first()
    )


def list_service_discounts(service_id: UUID) -> QuerySet[ServiceDiscount]:
    return ServiceDiscount.objects.filter(service_id=service_id)
