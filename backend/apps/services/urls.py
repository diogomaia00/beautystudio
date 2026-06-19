from django.urls import path

from .views import CategoryListView, ServiceDetailView, ServiceListView

app_name = "services"

# Client app catalog (mounted under /v1/) — public, read-only.
urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("", ServiceListView.as_view(), name="service-list"),
    path("<uuid:service_id>/", ServiceDetailView.as_view(), name="service-detail"),
]
