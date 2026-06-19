from django.contrib import admin

from .models import BoAlert, NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("recipient", "channel", "subject", "status", "created_at")
    list_filter = ("channel", "status")
    search_fields = ("subject", "dedup_key")
    readonly_fields = ("created_at",)


@admin.register(BoAlert)
class BoAlertAdmin(admin.ModelAdmin):
    list_display = ("staff", "alert_type", "title", "is_read", "created_at")
    list_filter = ("alert_type", "is_read")
    autocomplete_fields = ("staff",)
