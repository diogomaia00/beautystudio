from django.contrib import admin

from .models import Appointment, AppointmentBatch


@admin.register(AppointmentBatch)
class AppointmentBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "created_at")
    search_fields = ("id",)
    autocomplete_fields = ("client",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "staff",
        "service",
        "status",
        "start_at",
        "end_at",
        "has_nail_art",
        "price_snapshot",
    )
    list_filter = ("status", "has_nail_art", "nail_art_option")
    date_hierarchy = "start_at"
    autocomplete_fields = ("client", "staff", "service", "batch")
    readonly_fields = (
        "price_snapshot",
        "is_quote_only_snapshot",
        "duration_minutes_snapshot",
        "created_at",
        "updated_at",
    )
