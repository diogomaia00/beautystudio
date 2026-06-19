"""Procrastinate customization hook.

The Procrastinate app itself is auto-configured by ``procrastinate.contrib.django``
and is available as ``procrastinate.contrib.django.app``. Tasks are auto-discovered
from each installed app's ``tasks.py``. We do **not** build our own ``App``.

This module exposes the optional ``on_app_ready`` hook, wired via the
``PROCRASTINATE_ON_APP_READY`` setting, where cross-cutting worker configuration
and task blueprints can be registered as the queue grows.

Run the worker with:  ``python manage.py procrastinate worker``
"""

import procrastinate


def on_app_ready(app: procrastinate.App) -> None:
    # Periodic jobs (appointment reminders, birthday SMS, monthly reports) are
    # declared with ``@app.periodic(cron=...)`` in their owning app's tasks.py
    # and discovered automatically. Hook in shared worker setup here when needed.
    return None
