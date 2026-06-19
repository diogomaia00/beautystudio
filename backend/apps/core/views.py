from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LivenessSerializer, ReadinessSerializer


class LivenessView(APIView):
    """Liveness probe — the process is up. No external dependencies checked."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    @extend_schema(responses=LivenessSerializer, tags=["health"])
    def get(self, request):
        return Response({"status": "ok"})


class ReadinessView(APIView):
    """Readiness probe — the app can serve traffic (database reachable)."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    @extend_schema(responses=ReadinessSerializer, tags=["health"])
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_ok = True
        except Exception:
            db_ok = False

        return Response(
            {"status": "ready" if db_ok else "unavailable", "database": db_ok},
            status=200 if db_ok else 503,
        )
