import datetime
from datetime import timedelta
from decimal import Decimal
from unittest import mock
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.appointments import services
from apps.appointments.models import Appointment
from apps.availability.models import StaffBreak, StaffSchedule, StaffTimeOff
from apps.services.models import Service, ServiceCategory
from apps.users.models import ClientServiceDuration, User
from common.constants import AppointmentStatus, CancelReason, NailArtOption, UserRole

LISBON = ZoneInfo("Europe/Lisbon")


def _next_weekday(base: datetime.date, target_py_weekday: int) -> datetime.date:
    """Return the next date (>= base+7) whose Python weekday() == target."""
    d = base + timedelta(days=7)
    while d.weekday() != target_py_weekday:
        d += timedelta(days=1)
    return d


@mock.patch("apps.notifications.services.notify_appointment_confirmation", lambda **k: None)
@mock.patch("apps.notifications.services.notify_waitlist_for_freed_time", lambda **k: None)
class CreateAppointmentTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            msisdn="+351900000001", role=UserRole.STAFF, email="s@x.pt", is_active=True
        )
        self.client_user = User.objects.create_user(
            msisdn="+351900000002", role=UserRole.CLIENT, email="c@x.pt"
        )
        self.category = ServiceCategory.objects.create(name="Unhas", slug="unhas")
        self.service = Service.objects.create(
            category=self.category,
            staff=self.staff,
            name="Manicure",
            duration_minutes=60,
            price=Decimal("20.00"),
            is_nail_service=True,
        )
        # Monday (py weekday 0) -> clinic weekday 2; 09:00–18:00 local.
        self.monday = _next_weekday(timezone.now().astimezone(LISBON).date(), 0)
        StaffSchedule.objects.create(
            staff=self.staff, weekday=2, start_time=datetime.time(9, 0), end_time=datetime.time(18, 0)
        )

    def _at(self, hour, minute=0):
        return datetime.datetime(
            self.monday.year, self.monday.month, self.monday.day, hour, minute, tzinfo=LISBON
        ).astimezone(datetime.timezone.utc)

    def test_creates_booked_appointment_with_price_snapshot(self):
        appt = services.create_appointment(
            client=self.client_user, service=self.service, start_at=self._at(10)
        )
        self.assertEqual(appt.status, AppointmentStatus.BOOKED)
        self.assertEqual(appt.price_snapshot, Decimal("20.00"))
        self.assertEqual(appt.duration_minutes_snapshot, 60)
        self.assertEqual(appt.end_at, appt.start_at + timedelta(minutes=60))

    def test_blacklisted_client_cannot_book(self):
        self.client_user.blacklisted = True
        self.client_user.save(update_fields=["blacklisted"])
        with self.assertRaises(ValidationError):
            services.create_appointment(
                client=self.client_user, service=self.service, start_at=self._at(10)
            )

    def test_overlapping_booking_rejected(self):
        services.create_appointment(
            client=self.client_user, service=self.service, start_at=self._at(10)
        )
        other = User.objects.create_user(msisdn="+351900000003", role=UserRole.CLIENT, email="o@x.pt")
        with self.assertRaises(ValidationError):
            services.create_appointment(
                client=other, service=self.service, start_at=self._at(10, 30)
            )

    def test_outside_working_hours_rejected(self):
        with self.assertRaises(ValidationError):
            services.create_appointment(
                client=self.client_user, service=self.service, start_at=self._at(8)
            )

    def test_break_window_rejected(self):
        StaffBreak.objects.create(
            staff=self.staff, weekday=2, start_time=datetime.time(13, 0), end_time=datetime.time(14, 0)
        )
        with self.assertRaises(ValidationError):
            services.create_appointment(
                client=self.client_user, service=self.service, start_at=self._at(13, 30)
            )

    def test_time_off_rejected(self):
        StaffTimeOff.objects.create(
            staff=self.staff, start_at=self._at(9), end_at=self._at(18)
        )
        with self.assertRaises(ValidationError):
            services.create_appointment(
                client=self.client_user, service=self.service, start_at=self._at(10)
            )

    def test_minimum_notice_rejected(self):
        soon = timezone.now() + timedelta(minutes=30)
        with self.assertRaises(ValidationError):
            services.create_appointment(
                client=self.client_user, service=self.service, start_at=soon
            )

    def test_nail_art_extends_duration(self):
        appt = services.create_appointment(
            client=self.client_user,
            service=self.service,
            start_at=self._at(10),
            nail_art_option=NailArtOption.COMPLEX,
        )
        self.assertEqual(appt.duration_minutes_snapshot, 90)  # 60 + 30
        self.assertTrue(appt.has_nail_art)

    def test_per_client_duration_override_applied(self):
        ClientServiceDuration.objects.create(
            client=self.client_user, service=self.service, duration_minutes=45
        )
        appt = services.create_appointment(
            client=self.client_user, service=self.service, start_at=self._at(10)
        )
        self.assertEqual(appt.duration_minutes_snapshot, 45)

    def test_idempotency_key_returns_same_appointment(self):
        a = services.create_appointment(
            client=self.client_user, service=self.service, start_at=self._at(10), idempotency_key="k1"
        )
        b = services.create_appointment(
            client=self.client_user, service=self.service, start_at=self._at(10), idempotency_key="k1"
        )
        self.assertEqual(a.id, b.id)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_daily_limit_enforced(self):
        for hour in (10, 12, 14):
            services.create_appointment(
                client=self.client_user, service=self.service, start_at=self._at(hour)
            )
        with self.assertRaises(ValidationError):
            services.create_appointment(
                client=self.client_user, service=self.service, start_at=self._at(16)
            )


@mock.patch("apps.notifications.services.notify_appointment_confirmation", lambda **k: None)
@mock.patch("apps.notifications.services.notify_waitlist_for_freed_time", lambda **k: None)
class LifecycleTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            msisdn="+351900000001", role=UserRole.STAFF, email="s@x.pt", is_active=True
        )
        self.client_user = User.objects.create_user(
            msisdn="+351900000002", role=UserRole.CLIENT, email="c@x.pt"
        )
        self.category = ServiceCategory.objects.create(name="Unhas", slug="unhas")
        self.service = Service.objects.create(
            category=self.category, staff=self.staff, name="Manicure",
            duration_minutes=60, price=Decimal("20.00"), is_nail_service=True,
        )
        self.monday = _next_weekday(timezone.now().astimezone(LISBON).date(), 0)
        StaffSchedule.objects.create(
            staff=self.staff, weekday=2, start_time=datetime.time(9, 0), end_time=datetime.time(18, 0)
        )

    def _at(self, hour, minute=0):
        return datetime.datetime(
            self.monday.year, self.monday.month, self.monday.day, hour, minute, tzinfo=LISBON
        ).astimezone(datetime.timezone.utc)

    def _book(self, hour=10):
        return services.create_appointment(
            client=self.client_user, service=self.service, start_at=self._at(hour)
        )

    def test_client_cancel_within_24h_blocked(self):
        appt = self._book()
        appt.start_at = timezone.now() + timedelta(hours=2)
        appt.end_at = appt.start_at + timedelta(hours=1)
        appt.save()
        with self.assertRaises(ValidationError):
            services.cancel_appointment(appointment=appt, reason=CancelReason.CLIENT)

    def test_staff_cancel_within_24h_allowed(self):
        appt = self._book()
        appt.start_at = timezone.now() + timedelta(hours=2)
        appt.end_at = appt.start_at + timedelta(hours=1)
        appt.save()
        appt = services.cancel_appointment(appointment=appt, reason=CancelReason.STAFF)
        self.assertEqual(appt.status, AppointmentStatus.CANCELED)
        self.assertEqual(appt.cancel_reason, CancelReason.STAFF)

    def test_reschedule_keeps_status_booked(self):
        appt = self._book(10)
        appt = services.reschedule_appointment(
            appointment=appt, new_start_at=self._at(11), by_client=True
        )
        self.assertEqual(appt.status, AppointmentStatus.BOOKED)
        self.assertEqual(appt.start_at, self._at(11))

    def test_mark_made_and_no_show(self):
        appt = self._book(10)
        made = services.mark_made(appointment=appt)
        self.assertEqual(made.status, AppointmentStatus.MADE)
        appt2 = self._book(12)
        ns = services.mark_no_show(appointment=appt2)
        self.assertEqual(ns.status, AppointmentStatus.NO_SHOW)

    def test_edit_nail_art_recomputes_end(self):
        appt = self._book(10)
        appt = services.edit_nail_art(appointment=appt, nail_art_option=NailArtOption.SIMPLE)
        self.assertEqual(appt.nail_art_option, NailArtOption.SIMPLE)
        self.assertEqual(appt.duration_minutes_snapshot, 75)  # 60 + 15
