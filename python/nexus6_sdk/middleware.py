"""Nexus6 Middleware — drop-in AI identity verification for FastAPI/Starlette.

Signature (default): RSA signature verification — agent proves identity with a
cryptographic signature. The api_key identifies the agent, the private key
signs the request, and the middleware verifies using the agent's public key.

Usage:
    from nexus6_sdk.middleware import Nexus6Middleware
    app.add_middleware(Nexus6Middleware)

Headers (from the agent):
    X-API-Key: nxs6_xxx
    X-Agent-Signature: base64(RSA_SHA256(method:path:timestamp))
    X-Agent-Timestamp: 1700000000

How it works:
    1. Extracts X-API-Key, X-Agent-Signature, X-Agent-Timestamp from headers
    2. Fetches the agent's public key from Nexus6 by api_key (cached 1 hour)
    3. Reconstructs the signed message: "METHOD:/path:timestamp"
    4. Verifies the RSA signature locally using the public key
    5. If valid, stores identity in request.state.ai_identity and continues
    6. If expired (>5 min) or invalid, returns 401 Unauthorized
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import httpx
import time
from typing import Optional, List, Callable, Dict
from threading import Lock

try:
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

import base64

DEFAULT_BASE_URL = "https://nexus-7xp6n.ondigitalocean.app"


class Nexus6Middleware(BaseHTTPMiddleware):
    """FastAPI middleware that verifies AI agent identity via RSA signature.

    app.add_middleware(Nexus6Middleware)

    Headers:
      - X-API-Key: nxs6_xxx  (identifies the agent)
      - X-Agent-Signature: base64(RSA_SHA256(method:path:timestamp))
      - X-Agent-Timestamp: 1700000000 (Unix timestamp, max 5 min age)

    How it works:
      1. Extracts X-API-Key, X-Agent-Signature, X-Agent-Timestamp from headers
      2. Fetches the agent's public key from Nexus6 (cached for 1 hour)
      3. Reconstructs the signed message: "METHOD:/path:timestamp"
      4. Verifies the RSA signature locally using the public key
      5. If valid, stores identity in request.state.ai_identity and continues
      6. If expired (>5 min) or invalid, returns 401 Unauthorized
    """

    def __init__(
        self,
        app,
        mode: str = "signature",
        base_url: str = DEFAULT_BASE_URL,
        exclude_paths: Optional[List[str]] = None,
        on_verified: Optional[Callable] = None,
        signature_max_age_seconds: int = 300,
    ):
        super().__init__(app)
        self.mode = mode
        self.base_url = base_url.rstrip("/")
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json", "/favicon.ico"]
        self.on_verified = on_verified
        self.signature_max_age_seconds = signature_max_age_seconds

        self._public_key_cache: Dict[str, tuple] = {}
        self._cache_lock = Lock()

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)

        if self.mode == "signature":
            return await self._dispatch_signature(request, call_next)

        return await self._dispatch_api_key_legacy(request, call_next)

    async def _dispatch_signature(self, request: Request, call_next):
        api_key = request.headers.get("X-API-Key")
        signature = request.headers.get("X-Agent-Signature")
        timestamp = request.headers.get("X-Agent-Timestamp")

        if not api_key:
            return await call_next(request)

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

        verified = await self._verify_signature(api_key, message, signature)

        if not verified.get("verified"):
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid AI identity signature", "details": verified.get("error", "")}
            )

        request.state.ai_identity = verified

        if self.on_verified:
            self.on_verified(request, verified)

        return await call_next(request)

    async def _dispatch_api_key_legacy(self, request: Request, call_next):
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return await call_next(request)

        verified = await self._verify_api_key_legacy(api_key)

        if not verified.get("verified"):
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid AI identity", "details": verified.get("error", "")}
            )

        request.state.ai_identity = verified

        if self.on_verified:
            self.on_verified(request, verified)

        return await call_next(request)

    async def _verify_api_key_legacy(self, api_key: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10) as http:
                resp = await http.post(
                    f"{self.base_url}/api/v1/identity/verify",
                    json={"api_key": api_key}
                )
                return resp.json()
        except Exception:
            return {"verified": False, "error": "Verification service unavailable"}

    async def _verify_signature(self, api_key: str, message: str, signature_b64: str) -> dict:
        if not CRYPTO_AVAILABLE:
            return {"verified": False, "error": "Signature verification requires cryptography package. Install it with: pip install cryptography"}

        public_key = await self._get_cached_public_key(api_key)

        if not public_key:
            return {"verified": False, "error": f"Public key not found or agent not registered. Ensure the agent has generated RSA keys."}

        is_valid = _verify_rsa_signature(public_key, message, signature_b64)

        if not is_valid:
            return {"verified": False, "error": "RSA signature verification failed"}

        return {
            "verified": True,
            "identity": {
                "api_key": api_key,
                "verified_by": "rsa-signature",
            }
        }

    async def _get_cached_public_key(self, api_key: str) -> Optional[str]:
        cache_entry = self._public_key_cache.get(api_key)
        if cache_entry:
            cached_key, cached_at = cache_entry
            if time.time() - cached_at < 3600:
                return cached_key

        public_key = await self._fetch_public_key(api_key)
        if public_key:
            with self._cache_lock:
                self._public_key_cache[api_key] = (public_key, time.time())

        return public_key

    async def _fetch_public_key(self, api_key: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=10) as http:
                resp = await http.get(
                    f"{self.base_url}/api/v1/keys/public",
                    params={"api_key": api_key}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success"):
                        return data["public_key"]
                return None
        except Exception:
            return None


def _verify_rsa_signature(public_key_pem: str, message: str, signature_b64: str) -> bool:
    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )

        signature = base64.b64decode(signature_b64)

        public_key.verify(
            signature,
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return True
    except Exception:
        return False