from django.urls import path

from .views import (
    AppointmentCancelView,
    AppointmentDetailView,
    AppointmentListCreateView,
    AppointmentNailArtBlockedView,
    AppointmentRescheduleView,
    BatchCreateView,
)

app_name = "appointments"

# Client app (mounted under /v1/appointments/).
urlpatterns = [
    path("", AppointmentListCreateView.as_view(), name="list-create"),
    path("batches/", BatchCreateView.as_view(), name="batch-create"),
    path("<uuid:appointment_id>/", AppointmentDetailView.as_view(), name="detail"),
    path("<uuid:appointment_id>/cancel/", AppointmentCancelView.as_view(), name="cancel"),
    path(
        "<uuid:appointment_id>/reschedule/",
        AppointmentRescheduleView.as_view(),
        name="reschedule",
    ),
    path(
        "<uuid:appointment_id>/nail-art/",
        AppointmentNailArtBlockedView.as_view(),
        name="nail-art-blocked",
    ),
]
