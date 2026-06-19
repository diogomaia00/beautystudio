import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.test import TestCase

from apps.appointments.models import Appointment
from apps.reports import services
from apps.reports.models import MonthlyReport
from apps.services.models import Service, ServiceCategory
from apps.users.models import User
from common.constants import AppointmentStatus, UserRole

LISBON = ZoneInfo("Europe/Lisbon")


class MonthlyReportTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            msisdn="+351900000001", role=UserRole.STAFF, email="s@x.pt", is_active=True
        )
        self.c1 = User.objects.create_user(msisdn="+351900000002", role=UserRole.CLIENT, email="c1@x.pt")
        self.c2 = User.objects.create_user(msisdn="+351900000003", role=UserRole.CLIENT, email="c2@x.pt")
        self.category = ServiceCategory.objects.create(name="Unhas", slug="unhas")
        self.manicure = Service.objects.create(
            category=self.category, staff=self.staff, name="Manicure",
            duration_minutes=60, price=Decimal("20.00"),
        )
        self.pedicure = Service.objects.create(
            category=self.category, staff=self.staff, name="Pedicure",
            duration_minutes=30, price=Decimal("10.00"),
        )

    def _made(self, client, service, day, hour, minutes):
        start = datetime.datetime(2026, 3, day, hour, 0, tzinfo=LISBON).astimezone(datetime.timezone.utc)
        return Appointment.objects.create(
            client=client, staff=self.staff, service=service,
            status=AppointmentStatus.MADE,
            start_at=start, end_at=start + datetime.timedelta(minutes=minutes),
            duration_minutes_snapshot=minutes, price_snapshot=service.price,
        )

    def test_generate_monthly_report_metrics(self):
        self._made(self.c1, self.manicure, 3, 10, 60)
        self._made(self.c2, self.manicure, 4, 10, 60)
        self._made(self.c1, self.pedicure, 5, 10, 30)
        # A canceled one must not count toward revenue/hours.
        canceled_start = datetime.datetime(2026, 3, 6, 10, 0, tzinfo=LISBON).astimezone(datetime.timezone.utc)
        Appointment.objects.create(
            client=self.c1, staff=self.staff, service=self.manicure,
            status=AppointmentStatus.CANCELED, start_at=canceled_start,
            end_at=canceled_start + datetime.timedelta(minutes=60),
            duration_minutes_snapshot=60, price_snapshot=Decimal("20.00"),
        )

        report = services.generate_monthly_report(staff=self.staff, year=2026, month=3)
        metrics = report.metrics

        self.assertEqual(metrics["appointments"]["made"], 3)
        self.assertEqual(metrics["appointments"]["canceled"], 1)
        self.assertEqual(metrics["hours_worked"], 2.5)  # 60+60+30 minutes
        self.assertEqual(metrics["distinct_clients"], 2)
        self.assertEqual(metrics["new_clients"], 2)
        self.assertEqual(metrics["revenue_total"], "50.00")  # 20+20+10
        self.assertEqual(metrics["top_services"][0]["service"], "Manicure")

    def test_generate_is_idempotent_upsert(self):
        self._made(self.c1, self.manicure, 3, 10, 60)
        services.generate_monthly_report(staff=self.staff, year=2026, month=3)
        services.generate_monthly_report(staff=self.staff, year=2026, month=3)
        self.assertEqual(MonthlyReport.objects.filter(staff=self.staff, year=2026, month=3).count(), 1)
