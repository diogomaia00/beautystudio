from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self) -> None:
        # Seed the single system_settings row after this app's migrations run,
        # so the singleton always exists once the schema is in place.
        def _seed_system_settings(sender, **kwargs):
            from .services import ensure_system_settings

            ensure_system_settings()

        post_migrate.connect(_seed_system_settings, sender=self)
