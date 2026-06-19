from __future__ import annotations

from typing import Optional
from uuid import UUID

from django.db.models import QuerySet

from common.constants import UserRole

from .models import ClientServiceDuration, StaffEducation, User


def get_user_by_msisdn(msisdn: str) -> Optional[User]:
    """Return the user with this msisdn, or ``None`` if no account exists."""
    return User.objects.filter(msisdn=msisdn).first()


def get_user_by_id(user_id: UUID) -> Optional[User]:
    return User.objects.filter(pk=user_id).first()


# ------------------------------------------------------------
# Staff
# ------------------------------------------------------------

def list_staff(*, bookable_only: bool = False) -> QuerySet[User]:
    """Staff members. ``bookable_only`` keeps only active (visible) staff."""
    qs = User.objects.filter(role=UserRole.STAFF)
    if bookable_only:
        qs = qs.filter(is_active=True)
    return qs.order_by("first_name", "last_name")


def get_staff(staff_id: UUID) -> Optional[User]:
    return User.objects.filter(pk=staff_id, role=UserRole.STAFF).first()


def list_staff_educations(staff_id: UUID) -> QuerySet[StaffEducation]:
    return StaffEducation.objects.filter(staff_id=staff_id)


def get_staff_education(staff_id: UUID, education_id: UUID) -> Optional[StaffEducation]:
    return StaffEducation.objects.filter(pk=education_id, staff_id=staff_id).first()


# ------------------------------------------------------------
# Clients
# ------------------------------------------------------------

def list_clients(*, search: str | None = None) -> QuerySet[User]:
    qs = User.objects.filter(role=UserRole.CLIENT)
    if search:
        qs = qs.filter(msisdn__icontains=search)
    return qs.order_by("first_name", "last_name")


def get_client(client_id: UUID) -> Optional[User]:
    return User.objects.filter(pk=client_id, role=UserRole.CLIENT).first()


def get_client_service_duration(client_id: UUID, service_id: UUID) -> Optional[int]:
    """The per-client duration override (minutes) for a service, or ``None``."""
    row = ClientServiceDuration.objects.filter(
        client_id=client_id, service_id=service_id
    ).first()
    return row.duration_minutes if row else None


def list_client_service_durations(client_id: UUID) -> QuerySet[ClientServiceDuration]:
    return ClientServiceDuration.objects.select_related("service").filter(
        client_id=client_id
    )


def list_clients_with_birthday(month: int, day: int) -> QuerySet[User]:
    """Active clients whose birthday falls on a given month/day (feeds birthday SMS)."""
    return User.objects.filter(
        role=UserRole.CLIENT,
        is_active=True,
        birthday__month=month,
        birthday__day=day,
    )
