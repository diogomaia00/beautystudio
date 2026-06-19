from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import ClientServiceDuration, OtpCode, StaffEducation, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin keyed on ``msisdn`` (the inherited ``username`` field is removed)."""

    ordering = ("msisdn",)
    list_display = ("msisdn", "email", "first_name", "last_name", "role", "is_active", "blacklisted")
    list_filter = ("role", "is_active", "blacklisted", "is_staff", "is_superuser")
    search_fields = ("msisdn", "email", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("msisdn", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "birthday")}),
        ("Beauty Studio", {"fields": ("role", "preferred_channel", "blacklisted")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("msisdn", "email", "role", "password1", "password2"),
            },
        ),
    )


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ("msisdn", "purpose", "user", "expires_at", "consumed_at", "attempts")
    list_filter = ("purpose",)
    search_fields = ("msisdn",)
    readonly_fields = ("code_hash", "created_at", "updated_at")


@admin.register(StaffEducation)
class StaffEducationAdmin(admin.ModelAdmin):
    list_display = ("title", "staff", "education_type", "provider", "completed_on")
    list_filter = ("education_type",)
    search_fields = ("title", "provider")
    autocomplete_fields = ("staff",)


@admin.register(ClientServiceDuration)
class ClientServiceDurationAdmin(admin.ModelAdmin):
    list_display = ("client", "service", "duration_minutes")
    autocomplete_fields = ("client", "service")
