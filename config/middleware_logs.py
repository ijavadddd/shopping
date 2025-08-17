import uuid
import time
from contextvars import ContextVar
from django.utils.deprecation import MiddlewareMixin
from django_user_agents.utils import get_user_agent
from ipware import get_client_ip

request_id_ctx = ContextVar("request_id", default="-")
duration_ctx = ContextVar("duration", default="-")
user_agent_ctx = ContextVar("user_agent", default="-")
ip_ctx = ContextVar("ip", default="-")


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
        request_id_ctx.set(request_id)
        user_agent_ctx.set(str(get_user_agent(request)).replace(" ", ""))
        client_ip, _ = get_client_ip(request)
        ip_ctx.set(str(client_ip))
        # Process request
        response = self.get_response(request)
        # Calculate duration in milliseconds
        duration_ms = (time.time() - start_time) * 1000
        duration_ctx.set(str(round(duration_ms, 2)))
        return super().__call__(request)
