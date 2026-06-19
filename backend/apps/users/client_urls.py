from django.urls import path

from .views import ClientProfileView, StaffPublicDetailView, StaffPublicListView

app_name = "users_client"

# Client app (mounted under /v1/): own profile + public staff pages.
urlpatterns = [
    path("profile/", ClientProfileView.as_view(), name="profile"),
    path("staff/", StaffPublicListView.as_view(), name="staff-public-list"),
    path("staff/<uuid:staff_id>/", StaffPublicDetailView.as_view(), name="staff-public-detail"),
]
