import datetime
from datetime import timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.availability import services
from apps.availability.models import StaffBreak, StaffSchedule, StaffTimeOff
from apps.services.models import Service, ServiceCategory
from apps.users.models import User
from common.constants import AppointmentStatus, UserRole

LISBON = ZoneInfo("Europe/Lisbon")


def _next_monday(base: datetime.date) -> datetime.date:
    d = base + timedelta(days=7)
    while d.weekday() != 0:
        d += timedelta(days=1)
    return d


class GenerateSlotsTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            msisdn="+351900000001", role=UserRole.STAFF, email="s@x.pt", is_active=True
        )
        self.category = ServiceCategory.objects.create(name="Unhas", slug="unhas")
        self.service = Service.objects.create(
            category=self.category, staff=self.staff, name="Manicure",
            duration_minutes=60, price=Decimal("20.00"),
        )
        self.monday = _next_monday(timezone.now().astimezone(LISBON).date())
        StaffSchedule.objects.create(
            staff=self.staff, weekday=2, start_time=datetime.time(9, 0), end_time=datetime.time(12, 0)
        )

    def _at(self, hour, minute=0):
        return datetime.datetime(
            self.monday.year, self.monday.month, self.monday.day, hour, minute, tzinfo=LISBON
        ).astimezone(datetime.timezone.utc)

    def _slots(self):
        return services.generate_slots(staff=self.staff, on_date=self.monday, duration_minutes=60)

    def test_generates_grid_within_window(self):
        slots = self._slots()
        # 09:00 → 11:00 inclusive at 15-min steps (60-min service in a 3h window).
        self.assertEqual(len(slots), 9)
        self.assertIn(self._at(9, 0), slots)
        self.assertIn(self._at(11, 0), slots)
        self.assertNotIn(self._at(11, 15), slots)

    def test_no_schedule_means_no_slots(self):
        StaffSchedule.objects.all().delete()
        self.assertEqual(self._slots(), [])

    def test_time_off_removes_all_slots(self):
        StaffTimeOff.objects.create(staff=self.staff, start_at=self._at(9), end_at=self._at(12))
        self.assertEqual(self._slots(), [])

    def test_break_removes_overlapping_slots(self):
        StaffBreak.objects.create(
            staff=self.staff, weekday=2, start_time=datetime.time(10, 0), end_time=datetime.time(10, 30)
        )
        slots = self._slots()
        # A 60-min block starting 09:30 or 10:00 overlaps the 10:00–10:30 break.
        self.assertNotIn(self._at(9, 30), slots)
        self.assertNotIn(self._at(10, 0), slots)

    def test_existing_appointment_blocks_slot(self):
        Appointment.objects.create(
            client=self.staff,  # any user; not under test here
            staff=self.staff,
            service=self.service,
            status=AppointmentStatus.BOOKED,
            start_at=self._at(10),
            end_at=self._at(11),
            duration_minutes_snapshot=60,
            price_snapshot=Decimal("20.00"),
        )
        slots = self._slots()
        self.assertNotIn(self._at(10, 0), slots)
        self.assertNotIn(self._at(9, 30), slots)
