from rest_framework import serializers

from . import services as services_layer
from .models import Service, ServiceCategory, ServiceDiscount


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ["id", "name", "slug", "description", "display_order"]


class StaffBriefSerializer(serializers.Serializer):
    """Minimal staff representation embedded in catalog responses."""

    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)


class ServiceSerializer(serializers.ModelSerializer):
    """Catalog output: includes the effective (possibly discounted) price."""

    staff = StaffBriefSerializer(read_only=True)
    category = ServiceCategorySerializer(read_only=True)
    effective_price = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "category",
            "staff",
            "duration_minutes",
            "price",
            "effective_price",
            "is_quote_only",
            "is_nail_service",
            "is_active",
        ]

    def get_effective_price(self, obj: Service):
        price = services_layer.effective_price(obj)
        return str(price) if price is not None else None


class ServiceWriteSerializer(serializers.Serializer):
    """BO create/update payload (validation only — no persistence)."""

    category_id = serializers.UUIDField()
    staff_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    duration_minutes = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    is_quote_only = serializers.BooleanField(default=False)
    is_nail_service = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)


class ServiceDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDiscount
        fields = [
            "id",
            "service",
            "percentage",
            "starts_at",
            "ends_at",
            "is_active",
        ]
        read_only_fields = ["id", "is_active"]
