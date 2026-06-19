import datetime
import logging
from zoneinfo import ZoneInfo

from django.conf import settings
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def clinic_tz() -> ZoneInfo:
    """The clinic's wall-clock timezone (``settings.CLINIC_TIMEZONE``)."""
    return ZoneInfo(settings.CLINIC_TIMEZONE)


def clinic_weekday(value: datetime.date) -> int:
    """Map a date to the clinic weekday encoding ``1=Sun, 2=Mon … 7=Sat``.

    This is the single source of truth for the (non-ISO) weekday convention used
    by ``staff_schedules`` / ``staff_breaks`` (see ``database.md``). No other code
    should compare a raw ``isoweekday()``/``weekday()`` to a stored weekday.
    """
    return (value.isoweekday() % 7) + 1


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "errors": response.data,
            "status_code": response.status_code,
        }
    return response
