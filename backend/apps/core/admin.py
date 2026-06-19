from django.contrib import admin

from .models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "booking_slot_minutes",
        "booking_horizon_days",
        "minimum_notice_hours",
        "max_appointments_per_day",
        "max_appointments_per_week",
        "max_appointments_per_batch",
        "updated_at",
    )

    def has_add_permission(self, request):
        # Singleton: only allow adding when no row exists yet.
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
