from unittest import mock

from django.test import TestCase

from apps.notifications import services
from apps.notifications.models import BoAlert, NotificationLog, NotificationStatus
from apps.users.models import User
from common.constants import BoAlertType, NotificationChannel, UserRole


class ChannelOrderTests(TestCase):
    def test_preferred_channel_is_tried_first(self):
        order = services._channel_order(NotificationChannel.EMAIL)
        self.assertEqual(order[0], NotificationChannel.EMAIL)
        # The rest of the cascade follows, without duplicating the preferred one.
        self.assertEqual(set(order), set(NotificationChannel.values))
        self.assertEqual(len(order), len(set(order)))

    def test_no_preference_uses_default_cascade(self):
        order = services._channel_order(None)
        self.assertEqual(order[0], NotificationChannel.WHATSAPP)


@mock.patch.object(services, "send_email")
@mock.patch.object(services, "send_sms")
@mock.patch.object(services, "send_whatsapp")
class SendToClientTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            msisdn="+351911111111",
            role=UserRole.CLIENT,
            email="c@example.com",
            preferred_channel=NotificationChannel.WHATSAPP,
        )

    def test_sends_via_preferred_channel_and_logs_sent(self, whatsapp, sms, email):
        log = services.send_to_client(client=self.client_user, subject="Hi", body="Olá")
        whatsapp.assert_called_once()
        sms.assert_not_called()
        self.assertEqual(log.status, NotificationStatus.SENT)
        self.assertEqual(log.channel, NotificationChannel.WHATSAPP)

    def test_falls_back_to_next_channel_on_failure(self, whatsapp, sms, email):
        whatsapp.side_effect = RuntimeError("provider down")
        log = services.send_to_client(client=self.client_user, subject="Hi", body="Olá")
        whatsapp.assert_called_once()
        sms.assert_called_once()
        self.assertEqual(log.status, NotificationStatus.SENT)
        self.assertEqual(log.channel, NotificationChannel.SMS)

    def test_dedup_key_prevents_double_send(self, whatsapp, sms, email):
        first = services.send_to_client(
            client=self.client_user, subject="Hi", body="Olá", dedup_key="reminder:1"
        )
        second = services.send_to_client(
            client=self.client_user, subject="Hi", body="Olá", dedup_key="reminder:1"
        )
        self.assertIsNotNone(first)
        self.assertIsNone(second)  # idempotent — already sent
        self.assertEqual(whatsapp.call_count, 1)
        self.assertEqual(NotificationLog.objects.filter(dedup_key="reminder:1").count(), 1)

    def test_all_channels_failing_logs_failed(self, whatsapp, sms, email):
        whatsapp.side_effect = RuntimeError("down")
        sms.side_effect = RuntimeError("down")
        email.side_effect = RuntimeError("down")
        log = services.send_to_client(client=self.client_user, subject="Hi", body="Olá")
        self.assertEqual(log.status, NotificationStatus.FAILED)


class BoAlertTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            msisdn="+351922222222", role=UserRole.STAFF, email="s@example.com", is_active=True
        )

    def test_create_bo_alert(self):
        alert = services.create_bo_alert(
            staff=self.staff, alert_type=BoAlertType.WAITLIST_JOIN, title="Nova entrada"
        )
        self.assertFalse(alert.is_read)
        self.assertEqual(alert.alert_type, BoAlertType.WAITLIST_JOIN)
        self.assertEqual(BoAlert.objects.filter(staff=self.staff).count(), 1)

    def test_mark_alert_read(self):
        alert = services.create_bo_alert(
            staff=self.staff, alert_type=BoAlertType.CUSTOM_REQUEST, title="Pedido"
        )
        updated = services.mark_alert_read(alert=alert)
        self.assertTrue(updated.is_read)
