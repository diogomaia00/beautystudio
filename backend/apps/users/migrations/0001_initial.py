# Generated for Beauty Studio — Phase 2 (auth: msisdn user + SMS OTP).

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import apps.users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("staff", "Staff"),
                            ("client", "Client"),
                        ],
                        default="client",
                        max_length=10,
                    ),
                ),
                ("msisdn", models.CharField(max_length=20, unique=True)),
                ("birthday", models.DateField(blank=True, null=True)),
                (
                    "preferred_channel",
                    models.CharField(
                        choices=[("email", "Email"), ("sms", "SMS")],
                        default="sms",
                        max_length=10,
                    ),
                ),
                ("blacklisted", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "db_table": "users_user",
            },
            managers=[
                ("objects", apps.users.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="OtpCode",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("msisdn", models.CharField(max_length=20)),
                ("code_hash", models.CharField(max_length=128)),
                (
                    "purpose",
                    models.CharField(
                        choices=[("login", "Login"), ("signup", "Signup")],
                        default="login",
                        max_length=20,
                    ),
                ),
                ("expires_at", models.DateTimeField()),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="otp_codes",
                        to="users.user",
                    ),
                ),
            ],
            options={
                "db_table": "otp_code",
            },
        ),
        migrations.AddIndex(
            model_name="otpcode",
            index=models.Index(
                fields=["user", "expires_at"], name="otp_user_expires_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="otpcode",
            index=models.Index(
                fields=["msisdn", "expires_at"], name="otp_msisdn_expires_idx"
            ),
        ),
    ]
