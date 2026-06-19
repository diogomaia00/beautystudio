"""Back office API surface — mounted at ``/bo/v1/``.

Staff/admin endpoints: services & pricing, schedules/availability, client
management, appointment lifecycle, BO alerts, and reports. All gated by role-based
permissions (see auth.md / common/permissions.py).
"""

from django.urls import include, path

app_name = "bo_v1"

urlpatterns = [
    # Authentication — same SMS OTP flow as the client app (ADR 0004); staff and
    # admin log in here. Authorization is role-based downstream.
    path("auth/", include("apps.users.urls")),
    # Client management + staff education.
    path("", include("apps.users.bo_urls")),
    # Services & pricing (incl. seasonal discounts, quote-only).
    path("services/", include("apps.services.bo_urls")),
    # Schedules, breaks, time-off, waitlist, custom requests.
    path("availability/", include("apps.availability.bo_urls")),
    # Appointment lifecycle (made/no-show/cancel/reschedule, Nail Art edit).
    path("appointments/", include("apps.appointments.bo_urls")),
    # In-app back-office alerts.
    path("notifications/", include("apps.notifications.bo_urls")),
    # Monthly reports.
    path("reports/", include("apps.reports.bo_urls")),
]
