from django.test import TestCase

from apps.core.models import SystemSettings
from apps.core.selectors import get_system_settings
from apps.core.services import ensure_system_settings, update_system_settings


class SystemSettingsTests(TestCase):
    def test_singleton_seeded_with_recommended_defaults(self):
        obj = ensure_system_settings()
        self.assertEqual(obj.pk, 1)
        self.assertEqual(obj.booking_slot_minutes, 15)
        self.assertEqual(obj.booking_horizon_days, 60)
        self.assertEqual(obj.minimum_notice_hours, 2)
        self.assertEqual(obj.max_appointments_per_day, 3)
        self.assertEqual(obj.max_appointments_per_week, 3)
        self.assertEqual(obj.max_appointments_per_batch, 3)

    def test_only_one_row_can_exist(self):
        ensure_system_settings()
        SystemSettings(booking_slot_minutes=30).save()
        self.assertEqual(SystemSettings.objects.count(), 1)
        self.assertEqual(SystemSettings.objects.get().booking_slot_minutes, 30)

    def test_get_system_settings_returns_singleton(self):
        ensure_system_settings()
        self.assertEqual(get_system_settings().pk, 1)

    def test_update_system_settings(self):
        update_system_settings(booking_slot_minutes=20, minimum_notice_hours=4)
        settings = get_system_settings()
        self.assertEqual(settings.booking_slot_minutes, 20)
        self.assertEqual(settings.minimum_notice_hours, 4)

    def test_singleton_is_not_deleted(self):
        ensure_system_settings()
        get_system_settings().delete()
        self.assertEqual(SystemSettings.objects.count(), 1)
