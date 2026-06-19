from django.contrib import admin

from .models import (
    CustomBookingRequest,
    StaffBreak,
    StaffSchedule,
    StaffTimeOff,
    Waitlist,
)


@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    list_display = ("staff", "weekday", "start_time", "end_time")
    list_filter = ("weekday",)
    autocomplete_fields = ("staff",)


@admin.register(StaffBreak)
class StaffBreakAdmin(admin.ModelAdmin):
    list_display = ("staff", "weekday", "start_time", "end_time", "reason")
    list_filter = ("weekday",)
    autocomplete_fields = ("staff",)


@admin.register(StaffTimeOff)
class StaffTimeOffAdmin(admin.ModelAdmin):
    list_display = ("staff", "start_at", "end_at", "reason")
    autocomplete_fields = ("staff",)


@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ("client", "staff", "service", "desired_start_at", "status")
    list_filter = ("status",)
    autocomplete_fields = ("client", "staff", "service")


@admin.register(CustomBookingRequest)
class CustomBookingRequestAdmin(admin.ModelAdmin):
    list_display = ("client", "staff", "service", "preferred_date", "status")
    list_filter = ("status",)
    autocomplete_fields = ("client", "staff", "service")
