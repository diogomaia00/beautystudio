from django.urls import path

from .views import AvailableSlotsView, CustomRequestCreateView, WaitlistJoinView

app_name = "availability"

# Client app (mounted under /v1/availability/).
urlpatterns = [
    path("slots/", AvailableSlotsView.as_view(), name="slots"),
    path("waitlist/", WaitlistJoinView.as_view(), name="waitlist-join"),
    path("custom-requests/", CustomRequestCreateView.as_view(), name="custom-request"),
]
