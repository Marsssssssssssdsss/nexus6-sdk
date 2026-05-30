"""Anexus Middleware — verify AI identity by X-Agent-ID header.

Usage:
    from anexus_sdk.middleware import AnexusMiddleware
    app.add_middleware(AnexusMiddleware)
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import httpx
import time
from typing import Optional, List, Callable, Dict
from threading import Lock

DEFAULT_BASE_URL = "https://nexus-7xp6n.ondigitalocean.app"


class AnexusMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        base_url: str = DEFAULT_BASE_URL,
        exclude_paths: Optional[List[str]] = None,
        on_verified: Optional[Callable] = None,
        audit_logging: bool = False,
        audit_level: str = "basic",
        service_provider: str = "",
    ):
        super().__init__(app)
        self.base_url = base_url.rstrip("/")
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json", "/favicon.ico"]
        self.on_verified = on_verified
        self.audit_logging = audit_logging
        self.audit_level = audit_level
        self.service_provider = service_provider

        self._verify_cache: Dict[str, tuple] = {}
        self._cache_lock = Lock()

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)

        agent_id = request.headers.get("X-Agent-ID")
        start_time = time.time()

        if not agent_id:
            response = await call_next(request)
            if self.audit_logging:
                await self._send_audit_log({
                    "agent_id": "anonymous",
                    "agent_name": "",
                    "service_provider": self.service_provider or "unknown",
                    "endpoint": path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "log_level": self.audit_level,
                })
            return response

        verified = await self._verify_identity(agent_id)

        if not verified.get("verified"):
            error_response = JSONResponse(
                status_code=401,
                content={"error": "Invalid AI identity", "details": verified.get("error", "")}
            )
            if self.audit_logging:
                await self._send_audit_log({
                    "agent_id": agent_id,
                    "agent_name": "",
                    "service_provider": self.service_provider or "unknown",
                    "endpoint": path,
                    "method": request.method,
                    "status_code": 401,
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "log_level": self.audit_level,
                })
            return error_response

        request.state.ai_identity = verified

        if self.on_verified:
            self.on_verified(request, verified)

        response = await call_next(request)

        if self.audit_logging:
            await self._send_audit_log({
                "agent_id": agent_id,
                "agent_name": verified.get("name", ""),
                "service_provider": self.service_provider or "unknown",
                "endpoint": path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": int((time.time() - start_time) * 1000),
                "log_level": self.audit_level,
            })

        return response

    async def _send_audit_log(self, record: dict):
        try:
            async with httpx.AsyncClient(timeout=2) as http:
                await http.post(
                    f"{self.base_url}/api/v1/call-history/record",
                    json=[record]
                )
        except Exception:
            pass

    async def _verify_identity(self, agent_id: str) -> dict:
        cache_entry = self._verify_cache.get(agent_id)
        if cache_entry:
            cached_result, cached_at = cache_entry
            if time.time() - cached_at < 3600:
                return cached_result

        result = await self._fetch_verify(agent_id)

        if result.get("verified"):
            with self._cache_lock:
                if len(self._verify_cache) > 10000:
                    oldest = min(self._verify_cache.keys(), key=lambda k: self._verify_cache[k][1])
                    del self._verify_cache[oldest]
                self._verify_cache[agent_id] = (result, time.time())

        return result

    async def _fetch_verify(self, agent_id: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10) as http:
                resp = await http.post(
                    f"{self.base_url}/api/v1/identity/verify",
                    json={"api_key": agent_id}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("verified"):
                        return {
                            "verified": True,
                            "identity_type": data.get("identity_type", "ai"),
                            "id": data["id"],
                            "name": data.get("name", data["id"]),
                            "role": data.get("role", "ai_agent"),
                        }
                return {"verified": False, "error": "Agent not found or invalid"}
        except httpx.TimeoutException:
            return {"verified": False, "error": "Verification timed out"}
        except Exception:
            return {"verified": False, "error": "Verification service unavailable"}