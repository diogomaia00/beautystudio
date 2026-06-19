"""Seed the service catalog and pricing from the bundled seed data (ADR 0001).

Idempotent: re-running updates existing rows (matched by staff + service name)
and creates missing ones. After seeding, the DB is the source of truth — edit
prices/durations in the BO, not here.

Usage:  python manage.py seed_prices
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.services import seed_data
from apps.services.models import Service, ServiceCategory
from apps.users.models import User
from common.constants import UserRole


class Command(BaseCommand):
    help = "Seed service categories, staff, services and prices (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        staff = self._seed_staff()
        categories = self._seed_categories()
        created, updated = self._seed_services(staff, categories)
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded catalog: {created} services created, {updated} updated, "
                f"{len(staff)} staff, {len(categories)} categories."
            )
        )

    def _seed_staff(self) -> dict:
        staff = {}
        for key, info in seed_data.STAFF.items():
            user = User.objects.filter(msisdn=info["msisdn"]).first()
            if user is None:
                user = User.objects.create_user(
                    msisdn=info["msisdn"],
                    role=UserRole.STAFF,
                    first_name=info["first_name"],
                    last_name=info["last_name"],
                    email=info["email"],
                    is_active=True,
                )
            staff[key] = user
        return staff

    def _seed_categories(self) -> dict:
        categories = {}
        for entry in seed_data.CATEGORIES:
            category, _ = ServiceCategory.objects.update_or_create(
                slug=entry["slug"],
                defaults={"name": entry["name"], "display_order": entry["display_order"]},
            )
            categories[entry["slug"]] = category
        return categories

    def _seed_services(self, staff: dict, categories: dict):
        created = updated = 0
        for (
            category_slug,
            staff_key,
            name,
            price,
            duration_minutes,
            is_quote_only,
            is_nail_service,
        ) in seed_data.SERVICES:
            _, was_created = Service.objects.update_or_create(
                staff=staff[staff_key],
                name=name,
                defaults={
                    "category": categories[category_slug],
                    "price": None if is_quote_only else Decimal(str(price)),
                    "duration_minutes": duration_minutes,
                    "is_quote_only": is_quote_only,
                    "is_nail_service": is_nail_service,
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        return created, updated
