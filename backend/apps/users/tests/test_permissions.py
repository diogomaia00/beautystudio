from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.users.models import User
from common.constants import UserRole
from common.permissions import IsAdmin, IsClient, IsStaffMember


class RolePermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(msisdn="+351900000001", role=UserRole.ADMIN)
        cls.staff = User.objects.create_user(msisdn="+351900000002", role=UserRole.STAFF)
        cls.client_user = User.objects.create_user(msisdn="+351900000003", role=UserRole.CLIENT)
        cls.factory = APIRequestFactory()

    def _check(self, permission, user):
        request = self.factory.get("/")
        request.user = user
        return permission().has_permission(request, view=None)

    def test_is_admin(self):
        self.assertTrue(self._check(IsAdmin, self.admin))
        self.assertFalse(self._check(IsAdmin, self.staff))
        self.assertFalse(self._check(IsAdmin, self.client_user))

    def test_is_staff_member_includes_admin(self):
        self.assertTrue(self._check(IsStaffMember, self.admin))
        self.assertTrue(self._check(IsStaffMember, self.staff))
        self.assertFalse(self._check(IsStaffMember, self.client_user))

    def test_is_client(self):
        self.assertTrue(self._check(IsClient, self.client_user))
        self.assertFalse(self._check(IsClient, self.staff))
        self.assertFalse(self._check(IsClient, self.admin))
