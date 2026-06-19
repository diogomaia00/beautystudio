"""Client app API surface — mounted at ``/v1/``.

Domain routes (appointments, services, availability, …) are wired here as each
app's client-facing endpoints come online in later phases.
"""

from django.urls import path  # noqa: F401

app_name = "v1"

urlpatterns: list = []
