# Generated for Beauty Studio — Phase 3 (appointments: bookings, batches, lifecycle, snapshots).

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AppointmentBatch",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="appointment_batches",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "appointments_batch", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("booked", "Booked"),
                            ("made", "Made"),
                            ("canceled", "Canceled"),
                            ("no_show", "No Show"),
                        ],
                        default="booked",
                        max_length=20,
                    ),
                ),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField()),
                ("notes", models.TextField(blank=True)),
                (
                    "nail_art_option",
                    models.CharField(
                        blank=True,
                        choices=[("simple", "Simple"), ("complex", "Complex")],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("has_nail_art", models.BooleanField(default=False)),
                (
                    "price_snapshot",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
                ),
                ("is_quote_only_snapshot", models.BooleanField(default=False)),
                ("duration_minutes_snapshot", models.PositiveIntegerField()),
                (
                    "cancel_reason",
                    models.CharField(
                        blank=True,
                        choices=[("client", "Client"), ("staff", "Staff")],
                        max_length=20,
                        null=True,
                    ),
                ),
                ("idempotency_key", models.CharField(blank=True, max_length=64, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "batch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="appointments",
                        to="appointments.appointmentbatch",
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="appointments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="staff_appointments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="appointments",
                        to="services.service",
                    ),
                ),
            ],
            options={"db_table": "appointments_appointment", "ordering": ["start_at"]},
        ),
        migrations.AddConstraint(
            model_name="appointment",
            constraint=models.CheckConstraint(
                check=models.Q(("end_at__gt", models.F("start_at"))),
                name="appointment_range_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="appointment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("idempotency_key__isnull", False)),
                fields=("idempotency_key",),
                name="uniq_appointment_idempotency_key",
            ),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["staff", "start_at"], name="appointment_staff_start_idx"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["client", "start_at"], name="appointment_client_start_idx"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["status", "start_at"], name="appointment_status_start_idx"),
        ),
    ]
