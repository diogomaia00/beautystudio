import logging

from .context import request_id_ctx


class RequestIdFilter(logging.Filter):
    """Inject the current request correlation id into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True
