import datetime
from datetime import timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.test import TestCase

from apps.analytics import selectors as analytics
from apps.appointments.models import Appointment
from apps.services.models import Service, ServiceCategory
from apps.users.models import User
from common.constants import AppointmentStatus, UserRole

LISBON = ZoneInfo("Europe/Lisbon")


class StaffMonthlyMetricsTests(TestCase):
    """compute_staff_monthly_metrics feeds the monthly report (see reports app)."""

    YEAR, MONTH = 2026, 5  # a fixed, stable past month

    def setUp(self):
        self.staff = User.objects.create_user(
            msisdn="+351900000001", role=UserRole.STAFF, email="s@x.pt", is_active=True
        )
        self.category = ServiceCategory.objects.create(name="Unhas", slug="unhas")
        self.manicure = Service.objects.create(
            category=self.category, staff=self.staff, name="Manicure",
            duration_minutes=60, price=Decimal("20.00"),
        )
        self.pedicure = Service.objects.create(
            category=self.category, staff=self.staff, name="Pedicure",
            duration_minutes=30, price=Decimal("15.00"),
        )
        self.c1 = User.objects.create_user(msisdn="+351900000002", role=UserRole.CLIENT, email="c1@x.pt")
        self.c2 = User.objects.create_user(msisdn="+351900000003", role=UserRole.CLIENT, email="c2@x.pt")

    def _make(self, client, service, day, hour, status=AppointmentStatus.MADE, year=None, month=None):
        start_local = datetime.datetime(
            year or self.YEAR, month or self.MONTH, day, hour, 0, tzinfo=LISBON
        )
        start_at = start_local.astimezone(datetime.timezone.utc)
        return Appointment.objects.create(
            client=client, staff=self.staff, service=service, status=status,
            start_at=start_at,
            end_at=start_at + timedelta(minutes=service.duration_minutes),
            price_snapshot=service.price,
            is_quote_only_snapshot=False,
            duration_minutes_snapshot=service.duration_minutes,
        )

    def test_aggregates_counts_hours_and_revenue(self):
        # Two made manicures (60m, 20€) + one made pedicure (30m, 15€) = 2.5h, 55€.
        self._make(self.c1, self.manicure, 5, 10)
        self._make(self.c2, self.manicure, 5, 12)
        self._make(self.c1, self.pedicure, 6, 10)
        # Noise that must not count toward revenue/hours.
        self._make(self.c1, self.manicure, 6, 12, status=AppointmentStatus.CANCELED)
        self._make(self.c2, self.manicure, 7, 10, status=AppointmentStatus.NO_SHOW)

        metrics = analytics.compute_staff_monthly_metrics(self.staff.id, self.YEAR, self.MONTH)

        self.assertEqual(metrics["appointments"]["made"], 3)
        self.assertEqual(metrics["appointments"]["canceled"], 1)
        self.assertEqual(metrics["appointments"]["no_show"], 1)
        self.assertEqual(metrics["hours_worked"], 2.5)
        self.assertEqual(metrics["revenue_total"], "55.00")
        self.assertEqual(metrics["distinct_clients"], 2)
        self.assertEqual(metrics["new_clients"], 2)  # neither client had a made appt before
        # Revenue per worked hour: 55 / 2.5 = 22.0
        self.assertEqual(metrics["revenue_per_hour"], 22.0)
        # Top service by count is the manicure (2 made).
        self.assertEqual(metrics["top_services"][0], {"service": "Manicure", "count": 2})

    def test_quote_only_appointment_adds_no_revenue(self):
        appt = self._make(self.c1, self.manicure, 5, 10)
        appt.is_quote_only_snapshot = True
        appt.price_snapshot = None
        appt.save()
        metrics = analytics.compute_staff_monthly_metrics(self.staff.id, self.YEAR, self.MONTH)
        self.assertEqual(metrics["revenue_total"], "0.00")
        self.assertEqual(metrics["appointments"]["made"], 1)

    def test_returning_client_not_counted_as_new(self):
        # A made appointment in the previous month makes c1 a returning client.
        self._make(self.c1, self.manicure, 15, 10, year=2026, month=4)
        self._make(self.c1, self.manicure, 5, 10)
        self._make(self.c2, self.manicure, 5, 12)
        metrics = analytics.compute_staff_monthly_metrics(self.staff.id, self.YEAR, self.MONTH)
        self.assertEqual(metrics["distinct_clients"], 2)
        self.assertEqual(metrics["new_clients"], 1)  # only c2 is new
