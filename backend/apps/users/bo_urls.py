from django.urls import path

from .views import (
    BoClientBlacklistView,
    BoClientDetailView,
    BoClientDurationDeleteView,
    BoClientDurationListCreateView,
    BoClientListView,
    BoStaffEducationDetailView,
    BoStaffEducationListCreateView,
)

app_name = "users_bo"

# Back office (mounted under /bo/v1/): client management + staff education.
urlpatterns = [
    path("clients/", BoClientListView.as_view(), name="client-list"),
    path("clients/<uuid:client_id>/", BoClientDetailView.as_view(), name="client-detail"),
    path(
        "clients/<uuid:client_id>/blacklist/",
        BoClientBlacklistView.as_view(),
        name="client-blacklist",
    ),
    path(
        "clients/<uuid:client_id>/durations/",
        BoClientDurationListCreateView.as_view(),
        name="client-duration-list",
    ),
    path(
        "clients/<uuid:client_id>/durations/<uuid:service_id>/",
        BoClientDurationDeleteView.as_view(),
        name="client-duration-delete",
    ),
    path(
        "staff/<uuid:staff_id>/educations/",
        BoStaffEducationListCreateView.as_view(),
        name="staff-education-list",
    ),
    path(
        "staff/<uuid:staff_id>/educations/<uuid:education_id>/",
        BoStaffEducationDetailView.as_view(),
        name="staff-education-detail",
    ),
]
