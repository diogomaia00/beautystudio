from django.urls import path

from .views import (
    CsrfView,
    CurrentUserView,
    LogoutView,
    OtpRequestView,
    OtpVerifyView,
)

app_name = "users"

# Auth surface, shared by the client app (/v1/auth/) and the BO (/bo/v1/auth/).
# Login is identical for all roles (SMS OTP — ADR 0004); authorization is what
# differs between surfaces and is enforced per-endpoint downstream.
auth_urlpatterns = [
    path("csrf/", CsrfView.as_view(), name="csrf"),
    path("otp/request/", OtpRequestView.as_view(), name="otp-request"),
    path("otp/verify/", OtpVerifyView.as_view(), name="otp-verify"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", CurrentUserView.as_view(), name="me"),
]

urlpatterns = auth_urlpatterns
