from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, Throttled, ValidationError

from apps.users import services
from apps.users.models import OtpCode, User
from common.constants import OTP_MAX_VERIFY_ATTEMPTS, UserRole

FIXED_CODE = "123456"


def _patch_code():
    return mock.patch.object(services, "_generate_code", return_value=FIXED_CODE)


@mock.patch.object(services, "send_sms")
class RequestOtpTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            msisdn="+351911111111", role=UserRole.CLIENT, email="c@example.com"
        )

    def test_login_request_issues_code_for_existing_user(self, send_sms):
        with _patch_code():
            otp = services.request_otp(msisdn="+351911111111", purpose="login")
        self.assertEqual(otp.user, self.client_user)
        self.assertEqual(otp.purpose, "login")
        self.assertNotEqual(otp.code_hash, FIXED_CODE)  # only a hash is stored
        send_sms.assert_called_once()

    def test_login_request_rejected_when_no_account(self, send_sms):
        with self.assertRaises(ValidationError):
            services.request_otp(msisdn="+351922222222", purpose="login")
        send_sms.assert_not_called()

    def test_login_request_rejected_when_inactive(self, send_sms):
        self.client_user.is_active = False
        self.client_user.save(update_fields=["is_active"])
        with self.assertRaises(PermissionDenied):
            services.request_otp(msisdn="+351911111111", purpose="login")

    def test_signup_request_rejected_when_account_exists(self, send_sms):
        with self.assertRaises(ValidationError):
            services.request_otp(msisdn="+351911111111", purpose="signup")

    def test_signup_request_creates_unbound_code(self, send_sms):
        with _patch_code():
            otp = services.request_otp(msisdn="+351933333333", purpose="signup")
        self.assertIsNone(otp.user)
        self.assertEqual(otp.purpose, "signup")

    def test_cooldown_blocks_rapid_repeat(self, send_sms):
        with _patch_code():
            services.request_otp(msisdn="+351911111111", purpose="login")
            with self.assertRaises(Throttled):
                services.request_otp(msisdn="+351911111111", purpose="login")

    def test_hourly_cap_blocks_after_max(self, send_sms):
        # Pre-seed max codes spaced past the cooldown but within the hour.
        now = timezone.now()
        for i in range(5):
            OtpCode.objects.create(
                user=self.client_user,
                msisdn="+351911111111",
                code_hash="x",
                purpose="login",
                expires_at=now + timedelta(minutes=5),
            )
        with self.assertRaises(Throttled):
            services.request_otp(msisdn="+351911111111", purpose="login")


@mock.patch.object(services, "send_sms")
class VerifyOtpTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            msisdn="+351911111111", role=UserRole.CLIENT, email="c@example.com"
        )

    def _issue(self, purpose="login", msisdn="+351911111111"):
        with _patch_code():
            return services.request_otp(msisdn=msisdn, purpose=purpose)

    def test_verify_success_returns_user(self, send_sms):
        self._issue()
        user = services.verify_otp(
            msisdn="+351911111111", code=FIXED_CODE, purpose="login"
        )
        self.assertEqual(user, self.user)

    def test_code_is_single_use(self, send_sms):
        self._issue()
        services.verify_otp(msisdn="+351911111111", code=FIXED_CODE, purpose="login")
        with self.assertRaises(ValidationError):
            services.verify_otp(msisdn="+351911111111", code=FIXED_CODE, purpose="login")

    def test_wrong_code_increments_attempts(self, send_sms):
        otp = self._issue()
        with self.assertRaises(ValidationError):
            services.verify_otp(msisdn="+351911111111", code="000000", purpose="login")
        otp.refresh_from_db()
        self.assertEqual(otp.attempts, 1)
        self.assertIsNone(otp.consumed_at)

    def test_attempts_cap_locks_code(self, send_sms):
        otp = self._issue()
        otp.attempts = OTP_MAX_VERIFY_ATTEMPTS
        otp.save(update_fields=["attempts"])
        with self.assertRaises(Throttled):
            services.verify_otp(msisdn="+351911111111", code=FIXED_CODE, purpose="login")

    def test_expired_code_rejected(self, send_sms):
        otp = self._issue()
        otp.expires_at = timezone.now() - timedelta(minutes=1)
        otp.save(update_fields=["expires_at"])
        with self.assertRaises(ValidationError):
            services.verify_otp(msisdn="+351911111111", code=FIXED_CODE, purpose="login")

    def test_signup_verify_creates_client(self, send_sms):
        self._issue(purpose="signup", msisdn="+351944444444")
        user = services.verify_otp(
            msisdn="+351944444444",
            code=FIXED_CODE,
            purpose="signup",
            signup_data={
                "first_name": "Ana",
                "last_name": "Silva",
                "email": "ana@example.com",
                "birthday": "1995-04-01",
            },
        )
        self.assertEqual(user.role, UserRole.CLIENT)
        self.assertEqual(user.msisdn, "+351944444444")
        self.assertFalse(user.has_usable_password())
