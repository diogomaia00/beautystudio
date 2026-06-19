from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.services import services
from apps.services.models import Service, ServiceCategory
from apps.users.models import User
from common.constants import UserRole


class PricingTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            msisdn="+351900000001", role=UserRole.STAFF, email="s@x.pt"
        )
        self.category = ServiceCategory.objects.create(name="Unhas", slug="unhas")
        self.service = Service.objects.create(
            category=self.category, staff=self.staff, name="Manicure",
            duration_minutes=60, price=Decimal("20.00"),
        )

    def test_effective_price_without_discount(self):
        self.assertEqual(services.effective_price(self.service), Decimal("20.00"))

    def test_effective_price_applies_active_discount(self):
        now = timezone.now()
        services.create_discount(
            service=self.service,
            percentage=Decimal("25"),
            starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=1),
        )
        self.assertEqual(services.effective_price(self.service), Decimal("15.00"))

    def test_inactive_window_discount_ignored(self):
        now = timezone.now()
        services.create_discount(
            service=self.service,
            percentage=Decimal("25"),
            starts_at=now + timedelta(days=5),
            ends_at=now + timedelta(days=10),
        )
        self.assertEqual(services.effective_price(self.service), Decimal("20.00"))

    def test_quote_only_has_no_effective_price(self):
        quote = Service.objects.create(
            category=self.category, staff=self.staff, name="Reparação",
            duration_minutes=15, price=None, is_quote_only=True,
        )
        self.assertIsNone(services.effective_price(quote))

    def test_create_service_price_invariant(self):
        with self.assertRaises(ValidationError):
            services.create_service(
                category=self.category, staff=self.staff, name="Bad",
                duration_minutes=30, price=None, is_quote_only=False,
            )

    def test_create_service_rejects_non_staff(self):
        client = User.objects.create_user(msisdn="+351900000009", role=UserRole.CLIENT, email="c@x.pt")
        with self.assertRaises(ValidationError):
            services.create_service(
                category=self.category, staff=client, name="X",
                duration_minutes=30, price=Decimal("10.00"),
            )
