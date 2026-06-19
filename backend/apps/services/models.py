import uuid

from django.conf import settings
from django.db import models


class ServiceCategory(models.Model):
    """A grouping of services (e.g. nails, depilação laser, estética, wellbeing)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services_category"
        verbose_name_plural = "Service categories"
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name


class Service(models.Model):
    """A treatment offered by exactly one staff member (see business-rules.md).

    Price is **nullable**: ``is_quote_only`` models "price on request" (the seed
    files' ``-1`` sentinel is never carried into the DB — see ADR 0001).
    Durations are stored in minutes; never as slots.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name="services",
    )
    # Each service is offered by exactly one staff member.
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="services",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_quote_only = models.BooleanField(default=False)
    # Nail services can carry a Nail Art add-on (extra minutes) at booking time.
    is_nail_service = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services_service"
        ordering = ["name"]
        constraints = [
            # A service either has a concrete price, or is quote-only with no price.
            models.CheckConstraint(
                name="service_price_xor_quote_only",
                check=(
                    models.Q(is_quote_only=True, price__isnull=True)
                    | models.Q(is_quote_only=False, price__isnull=False)
                ),
            ),
        ]
        indexes = [
            models.Index(fields=["staff", "is_active"], name="service_staff_active_idx"),
            models.Index(fields=["category"], name="service_category_idx"),
        ]

    def __str__(self) -> str:
        return self.name


class ServiceDiscount(models.Model):
    """A time-bounded percentage discount on a service (seasonal, BO-managed).

    The effective (discounted) price is what gets snapshotted at booking time
    (see business-rules.md / ADR 0001).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="discounts",
    )
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services_discount"
        ordering = ["-starts_at"]
        constraints = [
            models.CheckConstraint(
                name="discount_percentage_range",
                check=models.Q(percentage__gt=0) & models.Q(percentage__lte=100),
            ),
            models.CheckConstraint(
                name="discount_window_valid",
                check=models.Q(ends_at__gt=models.F("starts_at")),
            ),
        ]
        indexes = [
            models.Index(fields=["service", "is_active"], name="discount_service_active_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.percentage}% off {self.service_id}"
