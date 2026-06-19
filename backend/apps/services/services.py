from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from django.db import transaction
from rest_framework.exceptions import ValidationError

from common.constants import UserRole

from . import selectors
from .models import Service, ServiceCategory, ServiceDiscount

TWO_PLACES = Decimal("0.01")


# ------------------------------------------------------------
# Pricing
# ------------------------------------------------------------

def effective_price(service: Service, at=None) -> Optional[Decimal]:
    """The price a client pays right now (default) or at ``at``.

    Returns ``None`` for quote-only services ("price on request"). Otherwise the
    base price minus any active seasonal discount, quantized to cents.
    """
    if service.is_quote_only or service.price is None:
        return None
    discount = selectors.get_active_discount(service, at)
    if discount is None:
        return service.price
    factor = (Decimal("100") - discount.percentage) / Decimal("100")
    return (service.price * factor).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


# ------------------------------------------------------------
# Categories
# ------------------------------------------------------------

@transaction.atomic
def create_category(*, name: str, slug: str, description: str = "", display_order: int = 0) -> ServiceCategory:
    category = ServiceCategory(
        name=name, slug=slug, description=description, display_order=display_order
    )
    category.full_clean()
    category.save()
    return category


@transaction.atomic
def update_category(*, category: ServiceCategory, **fields) -> ServiceCategory:
    for field, value in fields.items():
        setattr(category, field, value)
    category.full_clean()
    category.save()
    return category


# ------------------------------------------------------------
# Services
# ------------------------------------------------------------

def _validate_price_invariant(*, price, is_quote_only: bool) -> None:
    if is_quote_only and price is not None:
        raise ValidationError("A quote-only service cannot have a price.")
    if not is_quote_only and price is None:
        raise ValidationError("A non quote-only service must have a price.")


def _validate_staff(staff) -> None:
    if getattr(staff, "role", None) not in (UserRole.STAFF, UserRole.ADMIN):
        raise ValidationError("Services can only be assigned to staff members.")


@transaction.atomic
def create_service(
    *,
    category: ServiceCategory,
    staff,
    name: str,
    duration_minutes: int,
    price: Optional[Decimal] = None,
    is_quote_only: bool = False,
    is_nail_service: bool = False,
    description: str = "",
    is_active: bool = True,
) -> Service:
    _validate_staff(staff)
    _validate_price_invariant(price=price, is_quote_only=is_quote_only)
    service = Service(
        category=category,
        staff=staff,
        name=name,
        description=description,
        duration_minutes=duration_minutes,
        price=price,
        is_quote_only=is_quote_only,
        is_nail_service=is_nail_service,
        is_active=is_active,
    )
    service.full_clean()
    service.save()
    return service


@transaction.atomic
def update_service(*, service: Service, **fields) -> Service:
    """Update a service. Price edits never rewrite past bookings (snapshots)."""
    if "staff" in fields:
        _validate_staff(fields["staff"])
    for field, value in fields.items():
        setattr(service, field, value)
    _validate_price_invariant(price=service.price, is_quote_only=service.is_quote_only)
    service.full_clean()
    service.save()
    return service


# ------------------------------------------------------------
# Seasonal discounts
# ------------------------------------------------------------

@transaction.atomic
def create_discount(*, service: Service, percentage: Decimal, starts_at, ends_at) -> ServiceDiscount:
    if service.is_quote_only:
        raise ValidationError("Cannot discount a quote-only service.")
    if ends_at <= starts_at:
        raise ValidationError("Discount end must be after its start.")
    if not (Decimal("0") < percentage <= Decimal("100")):
        raise ValidationError("Discount percentage must be between 0 and 100.")
    discount = ServiceDiscount(
        service=service,
        percentage=percentage,
        starts_at=starts_at,
        ends_at=ends_at,
        is_active=True,
    )
    discount.full_clean()
    discount.save()
    return discount


@transaction.atomic
def deactivate_discount(*, discount: ServiceDiscount) -> ServiceDiscount:
    discount.is_active = False
    discount.save(update_fields=["is_active", "updated_at"])
    return discount
