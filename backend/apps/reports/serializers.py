from rest_framework import serializers

from .models import MonthlyReport


class MonthlyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyReport
        fields = ["id", "staff", "year", "month", "metrics", "generated_at"]


class GenerateReportSerializer(serializers.Serializer):
    year = serializers.IntegerField(min_value=2000, max_value=2100)
    month = serializers.IntegerField(min_value=1, max_value=12)
    staff_id = serializers.UUIDField(required=False)
