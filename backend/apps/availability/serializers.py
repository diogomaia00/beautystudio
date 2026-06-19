from rest_framework import serializers

from common.constants import (
    CustomRequestStatus,
    NailArtOption,
    WaitlistStatus,
)

from .models import (
    CustomBookingRequest,
    StaffBreak,
    StaffSchedule,
    StaffTimeOff,
    Waitlist,
)


# ------------------------------------------------------------
# Schedules / breaks / time-off
# ------------------------------------------------------------

class StaffScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffSchedule
        fields = ["id", "weekday", "start_time", "end_time"]


class WeeklyScheduleEntrySerializer(serializers.Serializer):
    weekday = serializers.IntegerField(min_value=1, max_value=7)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()


class WeeklyScheduleWriteSerializer(serializers.Serializer):
    entries = WeeklyScheduleEntrySerializer(many=True)


class StaffBreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffBreak
        fields = ["id", "weekday", "start_time", "end_time", "reason"]
        read_only_fields = ["id"]


class StaffTimeOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffTimeOff
        fields = ["id", "start_at", "end_at", "reason"]
        read_only_fields = ["id"]


# ------------------------------------------------------------
# Slots (client booking flow)
# ------------------------------------------------------------

class SlotQuerySerializer(serializers.Serializer):
    staff_id = serializers.UUIDField()
    service_id = serializers.UUIDField()
    date = serializers.DateField()
    nail_art = serializers.ChoiceField(
        choices=NailArtOption.choices, required=False, allow_null=True
    )


# ------------------------------------------------------------
# Waitlist
# ------------------------------------------------------------

class WaitlistJoinSerializer(serializers.Serializer):
    service_id = serializers.UUIDField()
    desired_start_at = serializers.DateTimeField()
    note = serializers.CharField(required=False, allow_blank=True, default="")


class WaitlistSerializer(serializers.ModelSerializer):
    client_msisdn = serializers.CharField(source="client.msisdn", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = Waitlist
        fields = [
            "id",
            "client",
            "client_msisdn",
            "service",
            "service_name",
            "desired_start_at",
            "status",
            "note",
            "created_at",
        ]


# ------------------------------------------------------------
# Custom booking requests
# ------------------------------------------------------------

class CustomRequestCreateSerializer(serializers.Serializer):
    service_id = serializers.UUIDField()
    preferred_date = serializers.DateField()
    preferred_time = serializers.TimeField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True, default="")


class CustomBookingRequestSerializer(serializers.ModelSerializer):
    client_msisdn = serializers.CharField(source="client.msisdn", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = CustomBookingRequest
        fields = [
            "id",
            "client",
            "client_msisdn",
            "service",
            "service_name",
            "preferred_date",
            "preferred_time",
            "status",
            "note",
            "created_at",
        ]


class StatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField()
