from django.urls import path

from .views import BoReportDetailView, BoReportGenerateView, BoReportListView

app_name = "reports"

# Back office (mounted under /bo/v1/reports/) — staff/admin only.
urlpatterns = [
    path("", BoReportListView.as_view(), name="list"),
    path("generate/", BoReportGenerateView.as_view(), name="generate"),
    path("<uuid:report_id>/", BoReportDetailView.as_view(), name="detail"),
]
