import logging
import time
from collections import deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


logger = logging.getLogger(__name__)


class GuardrailsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_request_size=10_000_000, requests_per_minute=100):
        super().__init__(app)
        self.max_request_size = max_request_size
        self.requests_per_minute = requests_per_minute
        self.request_times = {}

    async def dispatch(self, request, call_next):
        client_ip = request.client.host if request.client else "unknown"

        if request.headers.get("content-length"):
            size = int(request.headers["content-length"])
            if size > self.max_request_size:
                return JSONResponse({"error": "Request too large"}, status_code=413)

        now = time.time()
        request_deque = self.request_times.setdefault(client_ip, deque())

        while request_deque and (now - request_deque[0] > 60):
            request_deque.popleft()

        if len(request_deque) >= self.requests_per_minute:
            return JSONResponse({"error": "Rate limit exceeded"}, status_code=429)

        request_deque.append(now)

        # ✅ GUARDRAIL: Cleanup old IP entries to prevent memory leak
        if len(self.request_times) > 1000:  # If tracking >1000 IPs
            # Find oldest IPs (smallest deque timestamps)
            oldest_ips = sorted(
                self.request_times.items(),
                key=lambda x: min(x[1]) if x[1] else 0
            )[:500]  # Remove oldest 500, keep newest 500

            for ip, _ in oldest_ips:
                del self.request_times[ip]

            logger.debug(f"🧹 Cleaned up IP cache: now tracking {len(self.request_times)} IPs")

        response = await call_next(request)
        return response
