from rest_framework import serializers

from common.constants import NailArtOption

from .models import Appointment


class AppointmentServiceBriefSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    is_nail_service = serializers.BooleanField(read_only=True)


class AppointmentSerializer(serializers.ModelSerializer):
    service = AppointmentServiceBriefSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "batch",
            "client",
            "staff",
            "service",
            "status",
            "start_at",
            "end_at",
            "notes",
            "nail_art_option",
            "has_nail_art",
            "price_snapshot",
            "is_quote_only_snapshot",
            "duration_minutes_snapshot",
            "cancel_reason",
            "created_at",
        ]


class BoAppointmentSerializer(AppointmentSerializer):
    """Back-office variant: adds the client's name + msisdn so staff can see
    who an appointment is for (the client app's payload stays unchanged)."""

    client_name = serializers.SerializerMethodField()
    client_msisdn = serializers.CharField(source="client.msisdn", read_only=True)

    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + ["client_name", "client_msisdn"]

    def get_client_name(self, obj: Appointment) -> str:
        client = obj.client
        full_name = f"{client.first_name} {client.last_name}".strip()
        return full_name or client.msisdn


class AppointmentCreateSerializer(serializers.Serializer):
    service_id = serializers.UUIDField()
    start_at = serializers.DateTimeField()
    nail_art_option = serializers.ChoiceField(
        choices=NailArtOption.choices, required=False, allow_null=True
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    idempotency_key = serializers.CharField(required=False, allow_blank=False, max_length=64)


class BatchItemSerializer(serializers.Serializer):
    service_id = serializers.UUIDField()
    start_at = serializers.DateTimeField()
    nail_art_option = serializers.ChoiceField(
        choices=NailArtOption.choices, required=False, allow_null=True
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class BatchCreateSerializer(serializers.Serializer):
    items = BatchItemSerializer(many=True)
    idempotency_key = serializers.CharField(required=False, allow_blank=False, max_length=64)


class RescheduleSerializer(serializers.Serializer):
    new_start_at = serializers.DateTimeField()


class NailArtEditSerializer(serializers.Serializer):
    nail_art_option = serializers.ChoiceField(
        choices=NailArtOption.choices, allow_null=True
    )
