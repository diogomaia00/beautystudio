from rest_framework import serializers

from .models import BoAlert


class BoAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoAlert
        fields = ["id", "alert_type", "title", "body", "is_read", "created_at"]
