"""Client app API surface — mounted at ``/v1/``.

Domain routes (appointments, services, availability, …) are wired here as each
app's client-facing endpoints come online in later phases.
"""

from django.urls import include, path

app_name = "v1"

urlpatterns = [
    # Authentication (SMS OTP login/sign-up, session, logout) — see auth.md.
    path("auth/", include("apps.users.urls")),
]
