from django.urls import path

from .views import LivenessView, ReadinessView

app_name = "core"

urlpatterns = [
    path("healthz/", LivenessView.as_view(), name="liveness"),
    path("readyz/", ReadinessView.as_view(), name="readiness"),
]
