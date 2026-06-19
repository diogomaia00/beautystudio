from django.urls import path

from .views import BoAlertListView, BoAlertMarkReadView

app_name = "notifications"

# Back office (mounted under /bo/v1/notifications/) — staff/admin only.
urlpatterns = [
    path("alerts/", BoAlertListView.as_view(), name="alert-list"),
    path("alerts/<uuid:alert_id>/read/", BoAlertMarkReadView.as_view(), name="alert-read"),
]
