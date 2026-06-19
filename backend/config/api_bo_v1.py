"""Back office API surface — mounted at ``/bo/v1/``.

Staff/admin routes (services & pricing, schedules, clients, reports, …) are wired
here as each app's back-office endpoints come online in later phases.
"""

from django.urls import path  # noqa: F401

app_name = "bo_v1"

urlpatterns: list = []
