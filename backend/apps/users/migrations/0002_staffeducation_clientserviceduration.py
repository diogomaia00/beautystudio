# Generated for Beauty Studio — Phase 3 (staff education + per-client duration override).

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StaffEducation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "education_type",
                    models.CharField(
                        choices=[
                            ("formation", "Formation"),
                            ("webinar", "Webinar"),
                            ("course", "Course"),
                            ("workshop", "Workshop"),
                            ("other", "Other"),
                        ],
                        default="formation",
                        max_length=20,
                    ),
                ),
                ("provider", models.CharField(max_length=255)),
                ("title", models.CharField(max_length=255)),
                ("completed_on", models.DateField()),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="educations",
                        to="users.user",
                    ),
                ),
            ],
            options={
                "db_table": "users_staff_education",
                "ordering": ["-completed_on"],
            },
        ),
        migrations.CreateModel(
            name="ClientServiceDuration",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("duration_minutes", models.PositiveIntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service_durations",
                        to="users.user",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="client_durations",
                        to="services.service",
                    ),
                ),
            ],
            options={
                "db_table": "users_client_service_duration",
            },
        ),
        migrations.AddIndex(
            model_name="staffeducation",
            index=models.Index(
                fields=["staff", "completed_on"], name="education_staff_date_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="clientserviceduration",
            constraint=models.UniqueConstraint(
                fields=["client", "service"], name="uniq_client_service_duration"
            ),
        ),
    ]
