# Generated for Beauty Studio — Phase 3 (availability: schedules, breaks, time-off, waitlist, custom requests).

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
            name="StaffSchedule",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("weekday", models.PositiveSmallIntegerField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedules",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "staff_schedules", "ordering": ["weekday", "start_time"]},
        ),
        migrations.CreateModel(
            name="StaffBreak",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("weekday", models.PositiveSmallIntegerField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("reason", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="breaks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "staff_breaks", "ordering": ["weekday", "start_time"]},
        ),
        migrations.CreateModel(
            name="StaffTimeOff",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField()),
                ("reason", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="time_off",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "staff_time_off", "ordering": ["-start_at"]},
        ),
        migrations.CreateModel(
            name="Waitlist",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("desired_start_at", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waiting", "Waiting"),
                            ("contacted", "Contacted"),
                            ("closed", "Closed"),
                        ],
                        default="waiting",
                        max_length=20,
                    ),
                ),
                ("note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="waitlist_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="waitlist_for_staff",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="waitlist_entries",
                        to="services.service",
                    ),
                ),
            ],
            options={"db_table": "availability_waitlist", "ordering": ["desired_start_at", "created_at"]},
        ),
        migrations.CreateModel(
            name="CustomBookingRequest",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("preferred_date", models.DateField()),
                ("preferred_time", models.TimeField(blank=True, null=True)),
                ("note", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("rejected", "Rejected"),
                            ("closed", "Closed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="custom_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="custom_requests_for_staff",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="custom_requests",
                        to="services.service",
                    ),
                ),
            ],
            options={"db_table": "availability_custom_request", "ordering": ["preferred_date", "created_at"]},
        ),
        migrations.AddConstraint(
            model_name="staffschedule",
            constraint=models.CheckConstraint(
                check=models.Q(("weekday__gte", 1)) & models.Q(("weekday__lte", 7)),
                name="schedule_weekday_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="staffschedule",
            constraint=models.CheckConstraint(
                check=models.Q(("end_time__gt", models.F("start_time"))),
                name="schedule_window_valid",
            ),
        ),
        migrations.AddIndex(
            model_name="staffschedule",
            index=models.Index(fields=["staff", "weekday"], name="schedule_staff_weekday_idx"),
        ),
        migrations.AddConstraint(
            model_name="staffbreak",
            constraint=models.CheckConstraint(
                check=models.Q(("weekday__gte", 1)) & models.Q(("weekday__lte", 7)),
                name="break_weekday_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="staffbreak",
            constraint=models.CheckConstraint(
                check=models.Q(("end_time__gt", models.F("start_time"))),
                name="break_window_valid",
            ),
        ),
        migrations.AddIndex(
            model_name="staffbreak",
            index=models.Index(fields=["staff", "weekday"], name="break_staff_weekday_idx"),
        ),
        migrations.AddConstraint(
            model_name="stafftimeoff",
            constraint=models.CheckConstraint(
                check=models.Q(("end_at__gt", models.F("start_at"))),
                name="time_off_window_valid",
            ),
        ),
        migrations.AddIndex(
            model_name="stafftimeoff",
            index=models.Index(
                fields=["staff", "start_at", "end_at"], name="time_off_staff_range_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="waitlist",
            index=models.Index(fields=["staff", "status"], name="waitlist_staff_status_idx"),
        ),
        migrations.AddIndex(
            model_name="waitlist",
            index=models.Index(fields=["desired_start_at"], name="waitlist_desired_idx"),
        ),
        migrations.AddIndex(
            model_name="custombookingrequest",
            index=models.Index(fields=["staff", "status"], name="custom_req_staff_status_idx"),
        ),
    ]
