"""Throttling behaviour (rate limiting — see backend.md, Phase 6.2).

The suite disables global throttling (config/settings/test.py) so unrelated
tests aren't rate-limited; these tests exercise the DRF throttles directly with
an explicit low ``rate`` (set on the throttle so it's independent of the
import-time-bound ``THROTTLE_RATES`` table).
"""

from django.core.cache import cache
from django.test import TestCase
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from apps.users.models import User
from common.constants import UserRole


class _AnonThrottle(AnonRateThrottle):
    rate = "3/min"


class _UserThrottle(UserRateThrottle):
    rate = "3/min"


class _AnonView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]
    throttle_classes = [_AnonThrottle]

    def get(self, request):
        return Response({"ok": True})


class _UserView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [_UserThrottle]

    def get(self, request):
        return Response({"ok": True})


class ThrottlingTests(TestCase):
    def setUp(self):
        cache.clear()  # throttle counters live in the cache
        self.factory = APIRequestFactory()

    def test_anon_requests_are_throttled_after_limit(self):
        view = _AnonView.as_view()
        for _ in range(3):
            self.assertEqual(view(self.factory.get("/ping")).status_code, 200)
        # 4th request within the window is rejected with 429.
        self.assertEqual(view(self.factory.get("/ping")).status_code, 429)

    def test_user_requests_are_throttled_per_account(self):
        view = _UserView.as_view()
        user = User.objects.create_user(
            msisdn="+351900000010", role=UserRole.CLIENT, email="t@x.pt"
        )
        for _ in range(3):
            request = self.factory.get("/ping")
            force_authenticate(request, user=user)
            self.assertEqual(view(request).status_code, 200)
        request = self.factory.get("/ping")
        force_authenticate(request, user=user)
        self.assertEqual(view(request).status_code, 429)
