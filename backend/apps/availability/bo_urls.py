from django.urls import path

from .views import (
    BoCustomRequestUpdateView,
    BoCustomRequestView,
    BoStaffBreakDeleteView,
    BoStaffBreakView,
    BoStaffScheduleView,
    BoStaffTimeOffDeleteView,
    BoStaffTimeOffView,
    BoWaitlistUpdateView,
    BoWaitlistView,
)

app_name = "availability"

# Back office (mounted under /bo/v1/availability/) — staff/admin only.
urlpatterns = [
    path("staff/<uuid:staff_id>/schedule/", BoStaffScheduleView.as_view(), name="schedule"),
    path("staff/<uuid:staff_id>/breaks/", BoStaffBreakView.as_view(), name="break-list"),
    path(
        "staff/<uuid:staff_id>/breaks/<uuid:break_id>/",
        BoStaffBreakDeleteView.as_view(),
        name="break-delete",
    ),
    path("staff/<uuid:staff_id>/time-off/", BoStaffTimeOffView.as_view(), name="time-off-list"),
    path(
        "staff/<uuid:staff_id>/time-off/<uuid:time_off_id>/",
        BoStaffTimeOffDeleteView.as_view(),
        name="time-off-delete",
    ),
    path("staff/<uuid:staff_id>/waitlist/", BoWaitlistView.as_view(), name="waitlist"),
    path(
        "staff/<uuid:staff_id>/waitlist/<uuid:waitlist_id>/",
        BoWaitlistUpdateView.as_view(),
        name="waitlist-update",
    ),
    path(
        "staff/<uuid:staff_id>/custom-requests/",
        BoCustomRequestView.as_view(),
        name="custom-request-list",
    ),
    path(
        "staff/<uuid:staff_id>/custom-requests/<uuid:request_id>/",
        BoCustomRequestUpdateView.as_view(),
        name="custom-request-update",
    ),
]
