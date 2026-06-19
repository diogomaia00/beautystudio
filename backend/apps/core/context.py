from contextvars import ContextVar

# Per-request correlation id, set by CorrelationIdMiddleware and read by the
# logging filter. Kept in its own module so both can import it without coupling.
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")
