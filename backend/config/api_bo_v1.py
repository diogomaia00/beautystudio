"""Back office API surface — mounted at ``/bo/v1/``.

Staff/admin routes (services & pricing, schedules, clients, reports, …) are wired
here as each app's back-office endpoints come online in later phases.
"""

from django.urls import include, path

app_name = "bo_v1"

urlpatterns = [
    # Authentication — same SMS OTP flow as the client app (ADR 0004); staff and
    # admin log in here. Authorization is role-based downstream.
    path("auth/", include("apps.users.urls")),
]
