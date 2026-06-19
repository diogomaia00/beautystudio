import uuid

from .context import request_id_ctx

REQUEST_ID_HEADER = "X-Request-ID"
_META_KEY = "HTTP_X_REQUEST_ID"


class CorrelationIdMiddleware:
    """Attach a correlation id to every request/response.

    Reuses an inbound ``X-Request-ID`` header when present (e.g. set by NGINX or
    an upstream caller), otherwise generates one. The id is exposed on
    ``request.request_id``, published to a contextvar for structured logging, and
    echoed back on the response.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.META.get(_META_KEY) or uuid.uuid4().hex
        request.request_id = request_id
        token = request_id_ctx.set(request_id)
        try:
            response = self.get_response(request)
        finally:
            request_id_ctx.reset(token)
        response[REQUEST_ID_HEADER] = request_id
        return response
