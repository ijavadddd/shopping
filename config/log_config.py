import logging
from config.middleware_logs import request_id_ctx, duration_ctx, user_agent_ctx, ip_ctx


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        record.duration = duration_ctx.get()
        record.user_agent = user_agent_ctx.get()
        record.ip = ip_ctx.get()
        return True


class HealthcheckFilter(logging.Filter):
    def filter(self, record):
        return "health" not in record.getMessage().lower()


class RedactPIIFilter(logging.Filter):
    SENSITIVE = {"password", "token", "authorization", "api-key"}

    def filter(self, record):
        args = record.args

        # If args is a dict, mask sensitive keys
        if isinstance(args, dict):
            record.args = {
                k: ("***" if k.lower() in self.SENSITIVE else v)
                for k, v in args.items()
            }

        # If args is a Mapping but not dict
        elif hasattr(args, "items"):
            try:
                data = dict(args.items())
                record.args = {
                    k: ("***" if k.lower() in self.SENSITIVE else v)
                    for k, v in data.items()
                }
            except Exception:
                pass  # leave args as-is

        # Otherwise leave record.args unchanged
        return True
