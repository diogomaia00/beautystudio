from django.core.validators import RegexValidator
from django.utils import timezone
from rest_framework import serializers

from common.constants import (
    MIN_SIGNUP_AGE_YEARS,
    OTP_CODE_LENGTH,
    EducationType,
    NotificationChannel,
    OtpPurpose,
)

from .models import ClientServiceDuration, StaffEducation

# E.164: optional leading +, leading non-zero digit, 7–15 digits total.
msisdn_validator = RegexValidator(
    regex=r"^\+?[1-9]\d{6,14}$",
    message="Enter a valid phone number in international (E.164) format.",
)


def validate_birthday(value):
    """Birthday must not be in the future and the person must be old enough.

    Minimum age is ``MIN_SIGNUP_AGE_YEARS`` (see business-rules.md).
    """
    today = timezone.localdate()
    if value > today:
        raise serializers.ValidationError("A data de nascimento não pode ser no futuro.")
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < MIN_SIGNUP_AGE_YEARS:
        raise serializers.ValidationError(
            f"É necessário ter pelo menos {MIN_SIGNUP_AGE_YEARS} anos para criar conta."
        )
    return value


class UserSerializer(serializers.Serializer):
    """Public representation of the authenticated user (for /auth/me)."""

    id = serializers.UUIDField(read_only=True)
    msisdn = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    birthday = serializers.DateField(read_only=True, allow_null=True)
    preferred_channel = serializers.CharField(read_only=True)


class OtpRequestSerializer(serializers.Serializer):
    msisdn = serializers.CharField(validators=[msisdn_validator])
    purpose = serializers.ChoiceField(
        choices=OtpPurpose.choices,
        default=OtpPurpose.LOGIN,
    )


class OtpVerifySerializer(serializers.Serializer):
    msisdn = serializers.CharField(validators=[msisdn_validator])
    code = serializers.CharField(min_length=OTP_CODE_LENGTH, max_length=OTP_CODE_LENGTH)
    purpose = serializers.ChoiceField(
        choices=OtpPurpose.choices,
        default=OtpPurpose.LOGIN,
    )
    # Required only for signup — the verified number becomes a new account.
    first_name = serializers.CharField(required=False, allow_blank=False)
    last_name = serializers.CharField(required=False, allow_blank=False)
    email = serializers.EmailField(required=False)
    birthday = serializers.DateField(required=False, validators=[validate_birthday])

    def validate(self, attrs):
        if attrs["purpose"] == OtpPurpose.SIGNUP:
            missing = [
                field
                for field in ("first_name", "last_name", "email", "birthday")
                if not attrs.get(field)
            ]
            if missing:
                raise serializers.ValidationError(
                    {field: "This field is required for sign-up." for field in missing}
                )
        return attrs

    def signup_data(self) -> dict:
        return {
            "first_name": self.validated_data["first_name"],
            "last_name": self.validated_data["last_name"],
            "email": self.validated_data["email"],
            "birthday": self.validated_data["birthday"],
        }


# ------------------------------------------------------------
# Client profile (self-service)
# ------------------------------------------------------------

class ClientProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    birthday = serializers.DateField(required=False, validators=[validate_birthday])
    preferred_channel = serializers.ChoiceField(
        choices=NotificationChannel.choices, required=False
    )


# ------------------------------------------------------------
# Staff education (public + BO)
# ------------------------------------------------------------

class StaffEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffEducation
        fields = [
            "id",
            "education_type",
            "provider",
            "title",
            "completed_on",
            "description",
        ]


class StaffEducationWriteSerializer(serializers.Serializer):
    education_type = serializers.ChoiceField(
        choices=EducationType.choices, default=EducationType.FORMATION
    )
    provider = serializers.CharField(max_length=255)
    title = serializers.CharField(max_length=255)
    completed_on = serializers.DateField()
    description = serializers.CharField(required=False, allow_blank=True, default="")


class StaffPublicSerializer(serializers.Serializer):
    """Public staff page representation (experience-facing)."""

    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    educations = StaffEducationSerializer(many=True, read_only=True)


# ------------------------------------------------------------
# BO client management
# ------------------------------------------------------------

class ClientSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    msisdn = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    birthday = serializers.DateField(read_only=True)
    preferred_channel = serializers.CharField(read_only=True)
    blacklisted = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)


class BlacklistSerializer(serializers.Serializer):
    blacklisted = serializers.BooleanField()


class ClientServiceDurationSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = ClientServiceDuration
        fields = ["id", "service", "service_name", "duration_minutes"]
        read_only_fields = ["id", "service_name"]


class ClientServiceDurationWriteSerializer(serializers.Serializer):
    service_id = serializers.UUIDField()
    duration_minutes = serializers.IntegerField(min_value=1)
