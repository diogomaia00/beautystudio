from django.contrib import admin

from .models import Service, ServiceCategory, ServiceDiscount


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "staff",
        "duration_minutes",
        "price",
        "is_quote_only",
        "is_nail_service",
        "is_active",
    )
    list_filter = ("category", "is_active", "is_quote_only", "is_nail_service")
    search_fields = ("name",)
    autocomplete_fields = ("staff",)


@admin.register(ServiceDiscount)
class ServiceDiscountAdmin(admin.ModelAdmin):
    list_display = ("service", "percentage", "starts_at", "ends_at", "is_active")
    list_filter = ("is_active",)
