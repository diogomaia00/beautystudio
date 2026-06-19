from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsStaffMember

from . import selectors, services
from .serializers import BoAlertSerializer


class BoAlertListView(APIView):
    """The calling staff member's back-office alerts."""

    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: BoAlertSerializer(many=True)}, tags=["bo-notifications"])
    def get(self, request):
        unread_only = request.query_params.get("unread_only") == "true"
        alerts = selectors.list_bo_alerts(request.user.id, unread_only=unread_only)
        return Response(BoAlertSerializer(alerts, many=True).data)


class BoAlertMarkReadView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(request=None, responses={200: BoAlertSerializer}, tags=["bo-notifications"])
    def post(self, request, alert_id):
        alert = selectors.get_bo_alert(request.user.id, alert_id)
        if alert is None:
            raise NotFound("Alert not found.")
        alert = services.mark_alert_read(alert=alert)
        return Response(BoAlertSerializer(alert).data)
