from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Client app API — /v1/  (routes added per phase)
    # path("v1/", include("apps.router")),
    # Back office API — /bo/v1/  (routes added per phase)
    # path("bo/v1/", include("apps.bo_router")),
]
