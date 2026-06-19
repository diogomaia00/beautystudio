import datetime
from decimal import Decimal

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.services.models import Service, ServiceCategory
from apps.users import selectors, services
from apps.users.models import ClientServiceDuration, StaffEducation, User
from common.constants import EducationType, NotificationChannel, UserRole


class ClientProfileTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            msisdn="+351900000002", role=UserRole.CLIENT, email="c@x.pt"
        )

    def test_update_allowed_fields(self):
        user = services.update_client_profile(
            client=self.client_user, preferred_channel=NotificationChannel.EMAIL
        )
        self.assertEqual(user.preferred_channel, NotificationChannel.EMAIL)

    def test_update_disallowed_field_rejected(self):
        with self.assertRaises(ValidationError):
            services.update_client_profile(client=self.client_user, msisdn="+351999999999")

    def test_set_and_clear_blacklist(self):
        services.set_blacklisted(client=self.client_user, blacklisted=True)
        self.client_user.refresh_from_db()
        self.assertTrue(self.client_user.blacklisted)
        services.set_blacklisted(client=self.client_user, blacklisted=False)
        self.client_user.refresh_from_db()
        self.assertFalse(self.client_user.blacklisted)


class DurationOverrideTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(msisdn="+351900000001", role=UserRole.STAFF, email="s@x.pt")
        self.client_user = User.objects.create_user(msisdn="+351900000002", role=UserRole.CLIENT, email="c@x.pt")
        self.category = ServiceCategory.objects.create(name="Unhas", slug="unhas")
        self.service = Service.objects.create(
            category=self.category, staff=self.staff, name="Manicure",
            duration_minutes=60, price=Decimal("20.00"),
        )

    def test_set_then_get_override(self):
        services.set_client_service_duration(
            client=self.client_user, service=self.service, duration_minutes=45
        )
        self.assertEqual(
            selectors.get_client_service_duration(self.client_user.id, self.service.id), 45
        )

    def test_set_override_upserts(self):
        services.set_client_service_duration(client=self.client_user, service=self.service, duration_minutes=45)
        services.set_client_service_duration(client=self.client_user, service=self.service, duration_minutes=50)
        self.assertEqual(ClientServiceDuration.objects.count(), 1)
        self.assertEqual(
            selectors.get_client_service_duration(self.client_user.id, self.service.id), 50
        )


class StaffEducationTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(msisdn="+351900000001", role=UserRole.STAFF, email="s@x.pt")

    def test_create_education(self):
        education = services.create_staff_education(
            staff=self.staff,
            education_type=EducationType.COURSE,
            provider="Academy",
            title="Gel advanced",
            completed_on=datetime.date(2025, 5, 1),
        )
        self.assertEqual(StaffEducation.objects.count(), 1)
        self.assertEqual(education.title, "Gel advanced")

    def test_education_rejected_for_client(self):
        client = User.objects.create_user(msisdn="+351900000002", role=UserRole.CLIENT, email="c@x.pt")
        with self.assertRaises(ValidationError):
            services.create_staff_education(
                staff=client, education_type=EducationType.COURSE,
                provider="X", title="Y", completed_on=datetime.date(2025, 5, 1),
            )
