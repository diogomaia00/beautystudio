from .models import SystemSettings


def get_system_settings() -> SystemSettings:
    """Return the singleton system settings row (read-only).

    The row is seeded post-migrate (see ``CoreConfig.ready``); callers that need
    a guaranteed-present row on a fresh DB should use
    ``services.ensure_system_settings`` instead.
    """
    return SystemSettings.objects.get(pk=1)
