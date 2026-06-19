from rest_framework import serializers

from .models import SystemSettings


class LivenessSerializer(serializers.Serializer):
    status = serializers.CharField()


class ReadinessSerializer(serializers.Serializer):
    status = serializers.CharField()
    database = serializers.BooleanField()


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = [
            "booking_slot_minutes",
            "booking_horizon_days",
            "minimum_notice_hours",
            "max_appointments_per_day",
            "max_appointments_per_week",
            "max_appointments_per_batch",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]
