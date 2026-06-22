from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users import selectors as users_selectors
from common.permissions import IsStaffMember

from . import selectors, services
from .serializers import (
    ServiceCategorySerializer,
    ServiceDiscountSerializer,
    ServiceSerializer,
    ServiceWriteSerializer,
)


# ============================================================
# Client app (/v1) — public, read-only catalog
# ============================================================

class CategoryListView(ListAPIView):
    """Browse service categories (public catalog)."""

    permission_classes = [AllowAny]
    serializer_class = ServiceCategorySerializer
    pagination_class = None

    def get_queryset(self):
        return selectors.list_categories()


class ServiceListView(ListAPIView):
    """Browse active services, optionally filtered by category or staff."""

    permission_classes = [AllowAny]
    serializer_class = ServiceSerializer
    # The catalog is a small, bounded reference list the UI consumes whole
    # (grouped into category tabs) — unpaginated, like CategoryListView above.
    pagination_class = None

    def get_queryset(self):
        return selectors.list_services(
            category_id=self.request.query_params.get("category_id") or None,
            staff_id=self.request.query_params.get("staff_id") or None,
            active_only=True,
        )


class ServiceDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ServiceSerializer

    def get_object(self):
        service = selectors.get_service(self.kwargs["service_id"])
        if service is None:
            raise NotFound("Service not found.")
        return service


# ============================================================
# Back office (/bo/v1) — staff/admin management
# ============================================================

class BoServiceListCreateView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: ServiceSerializer(many=True)}, tags=["bo-services"])
    def get(self, request):
        qs = selectors.list_services(
            category_id=request.query_params.get("category_id") or None,
            staff_id=request.query_params.get("staff_id") or None,
            active_only=request.query_params.get("active_only", "false") == "true",
        )
        return Response(ServiceSerializer(qs, many=True).data)

    @extend_schema(request=ServiceWriteSerializer, responses={201: ServiceSerializer}, tags=["bo-services"])
    def post(self, request):
        data = ServiceWriteSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        payload = data.validated_data

        category = selectors.get_category(payload["category_id"])
        if category is None:
            raise NotFound("Category not found.")
        staff = users_selectors.get_user_by_id(payload["staff_id"])
        if staff is None:
            raise NotFound("Staff member not found.")

        service = services.create_service(
            category=category,
            staff=staff,
            name=payload["name"],
            description=payload.get("description", ""),
            duration_minutes=payload["duration_minutes"],
            price=payload.get("price"),
            is_quote_only=payload["is_quote_only"],
            is_nail_service=payload["is_nail_service"],
            is_active=payload["is_active"],
        )
        return Response(ServiceSerializer(service).data, status=status.HTTP_201_CREATED)


class BoServiceDetailView(APIView):
    permission_classes = [IsStaffMember]

    def _get(self, service_id):
        service = selectors.get_service(service_id)
        if service is None:
            raise NotFound("Service not found.")
        return service

    @extend_schema(responses={200: ServiceSerializer}, tags=["bo-services"])
    def get(self, request, service_id):
        return Response(ServiceSerializer(self._get(service_id)).data)

    @extend_schema(request=ServiceWriteSerializer, responses={200: ServiceSerializer}, tags=["bo-services"])
    def patch(self, request, service_id):
        service = self._get(service_id)
        data = ServiceWriteSerializer(data=request.data, partial=True)
        data.is_valid(raise_exception=True)
        fields = dict(data.validated_data)

        if "category_id" in fields:
            category = selectors.get_category(fields.pop("category_id"))
            if category is None:
                raise NotFound("Category not found.")
            fields["category"] = category
        if "staff_id" in fields:
            staff = users_selectors.get_user_by_id(fields.pop("staff_id"))
            if staff is None:
                raise NotFound("Staff member not found.")
            fields["staff"] = staff

        service = services.update_service(service=service, **fields)
        return Response(ServiceSerializer(service).data)


class BoDiscountListCreateView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={200: ServiceDiscountSerializer(many=True)}, tags=["bo-services"])
    def get(self, request, service_id):
        return Response(
            ServiceDiscountSerializer(
                selectors.list_service_discounts(service_id), many=True
            ).data
        )

    @extend_schema(request=ServiceDiscountSerializer, responses={201: ServiceDiscountSerializer}, tags=["bo-services"])
    def post(self, request, service_id):
        service = selectors.get_service(service_id)
        if service is None:
            raise NotFound("Service not found.")
        data = ServiceDiscountSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        discount = services.create_discount(
            service=service,
            percentage=data.validated_data["percentage"],
            starts_at=data.validated_data["starts_at"],
            ends_at=data.validated_data["ends_at"],
        )
        return Response(
            ServiceDiscountSerializer(discount).data, status=status.HTTP_201_CREATED
        )


class BoDiscountDeleteView(APIView):
    permission_classes = [IsStaffMember]

    @extend_schema(responses={204: OpenApiResponse(description="Discount deactivated")}, tags=["bo-services"])
    def delete(self, request, service_id, discount_id):
        discount = selectors.list_service_discounts(service_id).filter(pk=discount_id).first()
        if discount is None:
            raise NotFound("Discount not found.")
        services.deactivate_discount(discount=discount)
        return Response(status=status.HTTP_204_NO_CONTENT)
