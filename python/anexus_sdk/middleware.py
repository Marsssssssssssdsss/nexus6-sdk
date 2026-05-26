"""Anexus Middleware — drop-in AI identity verification for FastAPI/Starlette.

Usage:
    from anexus_sdk.middleware import AnexusMiddleware
    app.add_middleware(AnexusMiddleware)

Headers (from the agent):
    X-API-Key: nxs6_xxx
    X-Agent-Signature: hex(HMAC-SHA256(agent_secret, "METHOD:/path:timestamp"))
    X-Agent-Timestamp: 1700000000

How it works:
    1. Extracts X-API-Key, X-Agent-Signature, X-Agent-Timestamp from headers
    2. Fetches the agent's secret from Anexus by api_key (cached 1 hour)
    3. Reconstructs the signed message: "METHOD:/path:timestamp"
    4. Verifies the HMAC signature locally
    5. If valid, stores identity in request.state.ai_identity and continues
    6. If expired (>5 min) or invalid, returns 401 Unauthorized
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import httpx
import time
import hmac
import hashlib
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
        signature_max_age_seconds: int = 300,
    ):
        super().__init__(app)
        self.base_url = base_url.rstrip("/")
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json", "/favicon.ico"]
        self.on_verified = on_verified
        self.signature_max_age_seconds = signature_max_age_seconds

        self._secret_cache: Dict[str, tuple] = {}
        self._cache_lock = Lock()

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return await call_next(request)

        signature = request.headers.get("X-Agent-Signature")
        timestamp = request.headers.get("X-Agent-Timestamp")

        if not signature or not timestamp:
            return JSONResponse(
                status_code=401,
                content={"error": "Missing signature headers", "details": "X-Agent-Signature and X-Agent-Timestamp are required when using X-API-Key"}
            )

        now = int(time.time())
        try:
            ts = int(timestamp)
            if abs(now - ts) > self.signature_max_age_seconds:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Signature expired", "details": f"Timestamp age exceeds {self.signature_max_age_seconds}s limit"}
                )
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid timestamp", "details": "X-Agent-Timestamp must be a Unix timestamp"}
            )

        method = request.method
        path = request.url.path
        message = f"{method}:{path}:{timestamp}"

        verified = await self._verify_hmac(api_key, message, signature)

        if not verified.get("verified"):
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid AI identity signature", "details": verified.get("error", "")}
            )

        request.state.ai_identity = verified

        if self.on_verified:
            self.on_verified(request, verified)

        return await call_next(request)

    async def _verify_hmac(self, api_key: str, message: str, signature_hex: str) -> dict:
        agent_secret = await self._get_cached_secret(api_key)

        if not agent_secret:
            return {"verified": False, "error": "Agent secret not found. Ensure the agent has registered with an agent_secret."}

        expected = hmac.new(agent_secret.encode(), message.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected, signature_hex):
            return {"verified": False, "error": "HMAC signature verification failed"}

        return {
            "verified": True,
            "identity": {
                "api_key": api_key,
                "verified_by": "hmac-signature",
            }
        }

    async def _get_cached_secret(self, api_key: str) -> Optional[str]:
        cache_entry = self._secret_cache.get(api_key)
        if cache_entry:
            cached_secret, cached_at = cache_entry
            if time.time() - cached_at < 3600:
                return cached_secret

        agent_secret = await self._fetch_agent_secret(api_key)
        if agent_secret:
            with self._cache_lock:
                self._secret_cache[api_key] = (agent_secret, time.time())

        return agent_secret

    async def _fetch_agent_secret(self, api_key: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=10) as http:
                resp = await http.get(
                    f"{self.base_url}/api/v1/keys/secret",
                    params={"api_key": api_key}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success"):
                        return data["agent_secret"]
                return None
        except Exception:
            return None