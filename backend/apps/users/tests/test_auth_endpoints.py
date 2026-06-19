from unittest import mock

from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users import services
from apps.users.models import User
from common.constants import UserRole

FIXED_CODE = "123456"

V1 = "/v1/auth"
BO = "/bo/v1/auth"


@mock.patch.object(services, "send_sms")
@mock.patch.object(services, "_generate_code", return_value=FIXED_CODE)
class OtpLoginFlowTests(APITestCase):
    def setUp(self):
        cache.clear()  # reset ScopedRateThrottle state between tests
        self.user = User.objects.create_user(
            msisdn="+351911111111", role=UserRole.CLIENT, email="c@example.com"
        )

    def test_full_login_flow_establishes_session(self, _code, _sms):
        resp = self.client.post(
            f"{V1}/otp/request/", {"msisdn": "+351911111111", "purpose": "login"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client.post(
            f"{V1}/otp/verify/",
            {"msisdn": "+351911111111", "code": FIXED_CODE, "purpose": "login"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["role"], UserRole.CLIENT)

        # Session cookie now lets /me succeed, then logout ends it.
        me = self.client.get(f"{V1}/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["msisdn"], "+351911111111")

        out = self.client.post(f"{V1}/logout/")
        self.assertEqual(out.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(self.client.get(f"{V1}/me/").status_code, status.HTTP_403_FORBIDDEN)

    def test_me_requires_authentication(self, _code, _sms):
        self.assertEqual(self.client.get(f"{V1}/me/").status_code, status.HTTP_403_FORBIDDEN)

    def test_verify_with_wrong_code_is_rejected(self, _code, _sms):
        self.client.post(f"{V1}/otp/request/", {"msisdn": "+351911111111", "purpose": "login"})
        resp = self.client.post(
            f"{V1}/otp/verify/",
            {"msisdn": "+351911111111", "code": "000000", "purpose": "login"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_msisdn_is_rejected(self, _code, _sms):
        resp = self.client.post(f"{V1}/otp/request/", {"msisdn": "not-a-number"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bo_surface_shares_auth(self, _code, _sms):
        self.client.post(f"{BO}/otp/request/", {"msisdn": "+351911111111", "purpose": "login"})
        resp = self.client.post(
            f"{BO}/otp/verify/",
            {"msisdn": "+351911111111", "code": FIXED_CODE, "purpose": "login"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_signup_flow_creates_account(self, _code, _sms):
        self.client.post(f"{V1}/otp/request/", {"msisdn": "+351955555555", "purpose": "signup"})
        resp = self.client.post(
            f"{V1}/otp/verify/",
            {
                "msisdn": "+351955555555",
                "code": FIXED_CODE,
                "purpose": "signup",
                "first_name": "Ana",
                "last_name": "Silva",
                "email": "ana@example.com",
                "birthday": "1995-04-01",
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(msisdn="+351955555555", role=UserRole.CLIENT).exists())

    def test_signup_requires_profile_fields(self, _code, _sms):
        self.client.post(f"{V1}/otp/request/", {"msisdn": "+351955555555", "purpose": "signup"})
        resp = self.client.post(
            f"{V1}/otp/verify/",
            {"msisdn": "+351955555555", "code": FIXED_CODE, "purpose": "signup"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
