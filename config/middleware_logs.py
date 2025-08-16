import uuid
import time
from contextvars import ContextVar
from django.utils.deprecation import MiddlewareMixin

request_id_ctx = ContextVar("request_id", default="-")
duration_ctx = ContextVar("duration", default="-")
headers_ctx = ContextVar("headers", default="-")


def redact_pii(data):
    sensitive = {"password", "token", "authorization", "api-key"}

    # Convert to dict if it's not already
    if not isinstance(data, dict):
        try:
            data = dict(data.items())
        except AttributeError:
            return data  # if not iterable, just return it as-is

    # Mask sensitive fields
    return {k: ("***" if k.lower() in sensitive else v) for k, v in data.items()}


class RequestIDMiddleware(MiddlewareMixin):

    def __call__(self, request):
        start_time = time.time()
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        headers_ctx.set(redact_pii(request.headers))
        request_id_ctx.set(request_id)
        # Process request
        response = self.get_response(request)
        # Calculate duration in milliseconds
        duration_ms = (time.time() - start_time) * 1000
        duration_ctx.set(str(round(duration_ms, 2)))
        return super().__call__(request)
