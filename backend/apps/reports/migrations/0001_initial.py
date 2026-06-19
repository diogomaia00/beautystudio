# Generated for Beauty Studio — Phase 3 (reports: monthly report).

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
            name="MonthlyReport",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("year", models.PositiveIntegerField()),
                ("month", models.PositiveSmallIntegerField()),
                ("metrics", models.JSONField()),
                ("generated_at", models.DateTimeField(auto_now=True)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="monthly_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "reports_monthly_report", "ordering": ["-year", "-month"]},
        ),
        migrations.AddConstraint(
            model_name="monthlyreport",
            constraint=models.UniqueConstraint(
                fields=("staff", "year", "month"), name="uniq_monthly_report_period"
            ),
        ),
        migrations.AddConstraint(
            model_name="monthlyreport",
            constraint=models.CheckConstraint(
                check=models.Q(("month__gte", 1)) & models.Q(("month__lte", 12)),
                name="monthly_report_month_range",
            ),
        ),
    ]
