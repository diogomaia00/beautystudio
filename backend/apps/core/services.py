from django.db import transaction

from .models import SystemSettings


def ensure_system_settings() -> SystemSettings:
    """Return the singleton system settings, creating it with defaults if absent.

    Idempotent — safe to call from the post-migrate hook on every migrate.
    """
    obj, _ = SystemSettings.objects.get_or_create(pk=1)
    return obj


@transaction.atomic
def update_system_settings(**fields) -> SystemSettings:
    """Update scheduling settings on the singleton row.

    Validates against the model before saving. Intended for the back office.
    """
    obj = ensure_system_settings()
    for field, value in fields.items():
        setattr(obj, field, value)
    obj.full_clean()
    obj.save()
    return obj
