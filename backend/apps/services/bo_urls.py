from django.urls import path

from .views import (
    BoDiscountDeleteView,
    BoDiscountListCreateView,
    BoServiceDetailView,
    BoServiceListCreateView,
)

app_name = "services"

# Back-office management (mounted under /bo/v1/) — staff/admin only.
urlpatterns = [
    path("", BoServiceListCreateView.as_view(), name="bo-service-list"),
    path("<uuid:service_id>/", BoServiceDetailView.as_view(), name="bo-service-detail"),
    path(
        "<uuid:service_id>/discounts/",
        BoDiscountListCreateView.as_view(),
        name="bo-discount-list",
    ),
    path(
        "<uuid:service_id>/discounts/<uuid:discount_id>/",
        BoDiscountDeleteView.as_view(),
        name="bo-discount-delete",
    ),
]
