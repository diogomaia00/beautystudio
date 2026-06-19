# Generated for Beauty Studio — Phase 3 (notifications: log + BO alerts).

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
            name="NotificationLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("channel", models.CharField(choices=[("email", "Email"), ("sms", "SMS")], max_length=10)),
                ("subject", models.CharField(blank=True, max_length=255)),
                ("body", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[("sent", "Sent"), ("skipped", "Skipped"), ("failed", "Failed")],
                        max_length=10,
                    ),
                ),
                ("dedup_key", models.CharField(blank=True, max_length=128, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "recipient",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "notifications_log", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="BoAlert",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "alert_type",
                    models.CharField(
                        choices=[
                            ("waitlist_join", "Waitlist join"),
                            ("custom_request", "Custom booking request"),
                        ],
                        max_length=20,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("body", models.TextField(blank=True)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bo_alerts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "notifications_bo_alert", "ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="notificationlog",
            constraint=models.UniqueConstraint(
                condition=models.Q(("dedup_key__isnull", False)),
                fields=("dedup_key",),
                name="uniq_notification_dedup_key",
            ),
        ),
        migrations.AddIndex(
            model_name="boalert",
            index=models.Index(fields=["staff", "is_read"], name="bo_alert_staff_read_idx"),
        ),
    ]
