"""Client app API surface — mounted at ``/v1/``.

Booking-facing endpoints for clients (catalog browse, availability, bookings,
profile). Authorization is enforced per-endpoint (most require the client role;
catalog and public staff pages are open).
"""

from django.urls import include, path

app_name = "v1"

urlpatterns = [
    # Authentication (SMS OTP login/sign-up, session, logout) — see auth.md.
    path("auth/", include("apps.users.urls")),
    # Client profile + public staff pages.
    path("", include("apps.users.client_urls")),
    # Service catalog (public, read-only).
    path("services/", include("apps.services.urls")),
    # Dynamic availability, waitlist, custom requests.
    path("availability/", include("apps.availability.urls")),
    # Appointments (create/list/cancel/reschedule, batches).
    path("appointments/", include("apps.appointments.urls")),
]
