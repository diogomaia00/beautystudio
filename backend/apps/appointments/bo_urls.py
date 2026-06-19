from django.urls import path

from .views import (
    BoAppointmentCancelView,
    BoAppointmentDetailView,
    BoAppointmentListView,
    BoAppointmentMarkMadeView,
    BoAppointmentMarkNoShowView,
    BoAppointmentNailArtView,
    BoAppointmentRescheduleView,
)

app_name = "appointments"

# Back office (mounted under /bo/v1/appointments/) — staff/admin only.
urlpatterns = [
    path("", BoAppointmentListView.as_view(), name="list"),
    path("<uuid:appointment_id>/", BoAppointmentDetailView.as_view(), name="detail"),
    path("<uuid:appointment_id>/made/", BoAppointmentMarkMadeView.as_view(), name="made"),
    path("<uuid:appointment_id>/no-show/", BoAppointmentMarkNoShowView.as_view(), name="no-show"),
    path("<uuid:appointment_id>/cancel/", BoAppointmentCancelView.as_view(), name="cancel"),
    path(
        "<uuid:appointment_id>/reschedule/",
        BoAppointmentRescheduleView.as_view(),
        name="reschedule",
    ),
    path("<uuid:appointment_id>/nail-art/", BoAppointmentNailArtView.as_view(), name="nail-art"),
]
