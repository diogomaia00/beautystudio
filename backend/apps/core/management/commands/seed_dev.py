"""Seed a full local-development dataset (idempotent, dev-only).

Builds on ``seed_prices`` (catalog + staff), then adds:

- an **admin** superuser (for Django ``/admin/``),
- a few sample **clients** (with birthdays + preferred channels),
- weekly **staff schedules** (Mon–Fri 09:00–18:00) + a lunch **break**,
- one upcoming **time-off** block,
- a handful of **appointments** — future ``booked`` (booked through the real
  service so conflict checks run) plus past ``made`` ones in the previous month
  so the monthly report has data,
- one **waitlist** entry and one **custom request** (each raises a BO alert).

Guardrail: refuses to run unless ``DEBUG`` is True — never create fake data in
production. Re-running updates/skips existing rows, so it is safe to repeat.

Usage::

    python manage.py seed_dev [--force]
"""

from __future__ import annotations

import datetime
from datetime import timedelta

from decouple import config
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.appointments import services as appointment_services
from apps.availability.models import StaffBreak, StaffSchedule, StaffTimeOff
from apps.availability import services as availability_services
from apps.services import seed_data
from apps.services.models import Service
from apps.users.models import User
from common.constants import AppointmentStatus, NotificationChannel, UserRole
from common.utils import clinic_tz, clinic_weekday

# (msisdn, first, last, birthday, preferred_channel) — fictitious clients.
SAMPLE_CLIENTS = [
    ("+351920000001", "Ana", "Costa", datetime.date(1994, 3, 14), NotificationChannel.WHATSAPP),
    ("+351920000002", "Beatriz", "Lopes", datetime.date(2001, 7, 2), NotificationChannel.SMS),
    ("+351920000003", "Carla", "Martins", datetime.date(1988, 11, 23), NotificationChannel.EMAIL),
]

# Working days in the clinic encoding (1=Sun … 7=Sat): Mon–Fri = 2..6.
WORK_WEEKDAYS = [2, 3, 4, 5, 6]
WORK_START = datetime.time(9, 0)
WORK_END = datetime.time(18, 0)
LUNCH_START = datetime.time(13, 0)
LUNCH_END = datetime.time(14, 0)


class Command(BaseCommand):
    help = "Seed a full local dev dataset (idempotent). Refuses to run unless DEBUG=True."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Run even when DEBUG is False (use with care; never against production).",
        )

    def handle(self, *args, **options):
        from django.conf import settings

        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                "seed_dev refuses to run with DEBUG=False. This creates fake data "
                "and must never touch production. Pass --force to override locally."
            )

        with transaction.atomic():
            # 1. Catalog + staff (idempotent).
            call_command("seed_prices")

            admin = self._seed_admin()
            clients = self._seed_clients()
            staff = self._seed_staff_lookup()
            self._seed_schedules(staff)
            self._seed_breaks(staff)
            self._seed_time_off(staff)
            booked = self._seed_future_appointments(clients, staff)
            made = self._seed_past_made_appointments(clients, staff)
            self._seed_engagement(clients, staff)

        self.stdout.write(
            self.style.SUCCESS(
                f"Dev seed complete: admin={admin.msisdn}, {len(clients)} clients, "
                f"{len(staff)} staff scheduled, {booked} future booked + {made} past made "
                "appointments, waitlist + custom request created."
            )
        )

    # ── Users ────────────────────────────────────────────────────────────────

    def _seed_admin(self) -> User:
        msisdn = config("SEED_ADMIN_MSISDN", default="+351900000000")
        password = config("SEED_ADMIN_PASSWORD", default="admin")
        admin = User.objects.filter(msisdn=msisdn).first()
        if admin is None:
            admin = User.objects.create_superuser(
                msisdn=msisdn,
                password=password,
                email=config("SEED_ADMIN_EMAIL", default="admin@beautystudio.pt"),
                first_name="Admin",
                last_name="Studio",
            )
        return admin

    def _seed_clients(self) -> list[User]:
        clients = []
        for msisdn, first, last, birthday, channel in SAMPLE_CLIENTS:
            client = User.objects.filter(msisdn=msisdn).first()
            if client is None:
                client = User.objects.create_user(
                    msisdn=msisdn,
                    role=UserRole.CLIENT,
                    first_name=first,
                    last_name=last,
                    email=f"{first.lower()}@example.com",
                    birthday=birthday,
                    preferred_channel=channel,
                    is_active=True,
                )
            clients.append(client)
        return clients

    def _seed_staff_lookup(self) -> list[User]:
        """The staff created by seed_prices, looked up by their seed msisdns."""
        msisdns = [info["msisdn"] for info in seed_data.STAFF.values()]
        return list(User.objects.filter(msisdn__in=msisdns, role=UserRole.STAFF))

    # ── Availability ───────────────────────────────────────────────────────────

    def _seed_schedules(self, staff: list[User]) -> None:
        for member in staff:
            for weekday in WORK_WEEKDAYS:
                StaffSchedule.objects.get_or_create(
                    staff=member,
                    weekday=weekday,
                    start_time=WORK_START,
                    defaults={"end_time": WORK_END},
                )

    def _seed_breaks(self, staff: list[User]) -> None:
        for member in staff:
            for weekday in WORK_WEEKDAYS:
                StaffBreak.objects.get_or_create(
                    staff=member,
                    weekday=weekday,
                    start_time=LUNCH_START,
                    defaults={"end_time": LUNCH_END, "reason": "Almoço"},
                )

    def _seed_time_off(self, staff: list[User]) -> None:
        if not staff:
            return
        # One upcoming all-day block for the first staff member, ~30 days out.
        tz = clinic_tz()
        day = (timezone.now().astimezone(tz) + timedelta(days=30)).date()
        start = datetime.datetime.combine(day, datetime.time(0, 0), tzinfo=tz)
        StaffTimeOff.objects.get_or_create(
            staff=staff[0],
            start_at=start,
            defaults={
                "end_at": start + timedelta(days=1),
                "reason": "Folga (seed)",
            },
        )

    # ── Appointments ─────────────────────────────────────────────────────────

    def _next_local_utc(self, weekday_clinic: int, hour: int, min_days_ahead: int = 3):
        """UTC datetime for the next clinic ``weekday`` at ``hour`` local time."""
        tz = clinic_tz()
        day = (timezone.now().astimezone(tz) + timedelta(days=min_days_ahead)).date()
        while clinic_weekday(day) != weekday_clinic:
            day += timedelta(days=1)
        local = datetime.datetime(day.year, day.month, day.day, hour, 0, tzinfo=tz)
        return local.astimezone(datetime.timezone.utc)

    def _pick_service(self, staff_member: User, *, nail: bool | None = None) -> Service | None:
        qs = Service.objects.filter(
            staff=staff_member, is_active=True, price__isnull=False
        )
        if nail is not None:
            qs = qs.filter(is_nail_service=nail)
        return qs.order_by("name").first()

    def _seed_future_appointments(self, clients: list[User], staff: list[User]) -> int:
        if not clients or not staff:
            return 0
        member = staff[0]
        service = self._pick_service(member)
        if service is None:
            self.stdout.write(self.style.WARNING("No priced service for staff — skipping bookings."))
            return 0

        created = 0
        # Monday 10:00 and Wednesday 14:00 — distinct days avoid any overlap.
        plan = [(clients[0], 2, 10, "seed-booked-1"), (clients[1 % len(clients)], 4, 14, "seed-booked-2")]
        for client, weekday, hour, key in plan:
            if Appointment.objects.filter(idempotency_key=key).exists():
                continue
            try:
                appointment_services.create_appointment(
                    client=client,
                    service=service,
                    start_at=self._next_local_utc(weekday, hour),
                    idempotency_key=key,
                )
                created += 1
            except Exception as exc:  # noqa: BLE001 — seed should be resilient
                self.stdout.write(self.style.WARNING(f"Skipped booking {key}: {exc}"))
        return created

    def _seed_past_made_appointments(self, clients: list[User], staff: list[User]) -> int:
        """Past ``made`` appointments (previous month) so the monthly report has data.

        Created directly via the ORM — the booking service only allows future
        times — with snapshots taken from the current service config.
        """
        if not clients or not staff:
            return 0
        member = staff[0]
        service = self._pick_service(member)
        if service is None:
            return 0

        tz = clinic_tz()
        now_local = timezone.now().astimezone(tz)
        # A weekday around the middle of the previous month.
        first_this_month = now_local.replace(day=1)
        prev_month_day = (first_this_month - timedelta(days=15)).date()
        while clinic_weekday(prev_month_day) not in WORK_WEEKDAYS:
            prev_month_day += timedelta(days=1)

        created = 0
        for index, client in enumerate(clients[:2]):
            key = f"seed-made-{index + 1}"
            if Appointment.objects.filter(idempotency_key=key).exists():
                continue
            local = datetime.datetime(
                prev_month_day.year,
                prev_month_day.month,
                prev_month_day.day,
                10 + index * 2,
                0,
                tzinfo=tz,
            )
            start_at = local.astimezone(datetime.timezone.utc)
            Appointment.objects.create(
                client=client,
                staff=member,
                service=service,
                status=AppointmentStatus.MADE,
                start_at=start_at,
                end_at=start_at + timedelta(minutes=service.duration_minutes),
                price_snapshot=service.price,
                is_quote_only_snapshot=service.is_quote_only,
                duration_minutes_snapshot=service.duration_minutes,
                idempotency_key=key,
            )
            created += 1
        return created

    # ── Engagement (waitlist + custom request) ─────────────────────────────────

    def _seed_engagement(self, clients: list[User], staff: list[User]) -> None:
        if not clients or not staff:
            return
        member = staff[0]
        service = self._pick_service(member)
        if service is None:
            return
        client = clients[-1]

        if not service.waitlist_entries.filter(client=client).exists():
            availability_services.join_waitlist(
                client=client,
                service=service,
                desired_start_at=self._next_local_utc(2, 11),
                note="Seed: gostava de um horário de manhã.",
            )

        if not service.custom_requests.filter(client=client).exists():
            tz = clinic_tz()
            far = (timezone.now().astimezone(tz) + timedelta(days=90)).date()
            availability_services.create_custom_request(
                client=client,
                service=service,
                preferred_date=far,
                preferred_time=datetime.time(15, 0),
                note="Seed: pedido para lá do horizonte de marcação.",
            )
