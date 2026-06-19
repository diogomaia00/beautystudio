# Generated for Beauty Studio — Phase 3 (services: catalog, pricing, discounts).

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceCategory",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("display_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "services_category",
                "verbose_name_plural": "Service categories",
                "ordering": ["display_order", "name"],
            },
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("duration_minutes", models.PositiveIntegerField()),
                (
                    "price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("is_quote_only", models.BooleanField(default=False)),
                ("is_nail_service", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="services",
                        to="services.servicecategory",
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="services",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "services_service",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ServiceDiscount",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("percentage", models.DecimalField(decimal_places=2, max_digits=5)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="discounts",
                        to="services.service",
                    ),
                ),
            ],
            options={
                "db_table": "services_discount",
                "ordering": ["-starts_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="service",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(("is_quote_only", True), ("price__isnull", True))
                    | models.Q(("is_quote_only", False), ("price__isnull", False))
                ),
                name="service_price_xor_quote_only",
            ),
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(
                fields=["staff", "is_active"], name="service_staff_active_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(fields=["category"], name="service_category_idx"),
        ),
        migrations.AddConstraint(
            model_name="servicediscount",
            constraint=models.CheckConstraint(
                check=models.Q(("percentage__gt", 0)) & models.Q(("percentage__lte", 100)),
                name="discount_percentage_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="servicediscount",
            constraint=models.CheckConstraint(
                check=models.Q(("ends_at__gt", models.F("starts_at"))),
                name="discount_window_valid",
            ),
        ),
        migrations.AddIndex(
            model_name="servicediscount",
            index=models.Index(
                fields=["service", "is_active"], name="discount_service_active_idx"
            ),
        ),
    ]
