from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users import selectors as users_selectors
from common.constants import UserRole
from common.permissions import IsStaffMember

from . import selectors, services
from .serializers import GenerateReportSerializer, MonthlyReportSerializer


def _resolve_staff(request, staff_id):
    """Staff see only their own reports; admin may target any staff member."""
    if request.user.role == UserRole.STAFF:
        return request.user
    # admin
    if staff_id is None:
        raise ValidationError("staff_id is required for admin.")
    staff = users_selectors.get_staff(staff_id)
    if staff is None:
        raise NotFound("Staff member not found.")
    return staff


class BoReportListView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: MonthlyReportSerializer(many=True)}, tags=["bo-reports"])
    def get(self, request):
        staff = _resolve_staff(request, request.query_params.get("staff_id"))
        return Response(MonthlyReportSerializer(selectors.list_reports(staff.id), many=True).data)


class BoReportDetailView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: MonthlyReportSerializer}, tags=["bo-reports"])
    def get(self, request, report_id):
        report = selectors.get_report(report_id)
        if report is None:
            raise NotFound("Report not found.")
        if request.user.role == UserRole.STAFF and report.staff_id != request.user.id:
            raise PermissionDenied("This report is not yours.")
        return Response(MonthlyReportSerializer(report).data)


class BoReportGenerateView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(request=GenerateReportSerializer, responses={201: MonthlyReportSerializer}, tags=["bo-reports"])
    def post(self, request):
        data = GenerateReportSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        staff = _resolve_staff(request, data.validated_data.get("staff_id"))
        report = services.generate_monthly_report(
            staff=staff,
            year=data.validated_data["year"],
            month=data.validated_data["month"],
        )
        return Response(MonthlyReportSerializer(report).data, status=status.HTTP_201_CREATED)
