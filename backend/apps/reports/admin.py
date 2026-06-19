from django.contrib import admin

from .models import MonthlyReport


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ("staff", "year", "month", "generated_at")
    list_filter = ("year", "month")
    autocomplete_fields = ("staff",)
    readonly_fields = ("metrics", "generated_at")
