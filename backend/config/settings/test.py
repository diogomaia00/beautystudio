"""Settings for the automated test suite.

Extends dev but neutralizes anything that would make tests slow or flaky:
throttling is disabled by default (individual tests opt back in with
``override_settings``), and a fast password hasher is used. Run with::

    python manage.py test --settings=config.settings.test
"""

from .dev import *  # noqa: F401, F403
from .dev import REST_FRAMEWORK

# Disable the global throttles so unrelated tests aren't rate-limited by the
# shared per-IP counter. Throttle behaviour itself is covered explicitly in
# apps/core/tests/test_throttling.py via @override_settings.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {"anon": None, "user": None, "otp": None},
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
