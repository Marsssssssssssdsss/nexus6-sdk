"""Anexus MCP Middleware — verify AI identity in MCP protocol transports."""

import httpx
import time
from typing import Optional, Dict, Any

DEFAULT_BASE_URL = "https://nexus-7xp6n.ondigitalocean.app"


class AnexusMCPMiddleware:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        reject_unverified: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.reject_unverified = reject_unverified
        self._verify_cache: Dict[str, tuple] = {}

    async def verify_identity(self, agent_id: str) -> dict:
        if not agent_id:
            return {"verified": False, "error": "No agent ID provided"}
        cache_entry = self._verify_cache.get(agent_id)
        if cache_entry:
            cached_result, cached_at = cache_entry
            if time.time() - cached_at < 3600:
                return cached_result
        try:
            async with httpx.AsyncClient(timeout=10) as http:
                resp = await http.post(
                    f"{self.base_url}/api/v1/identity/verify",
                    json={"api_key": agent_id}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    result = {
                        "verified": data.get("verified", False),
                        "identity_type": data.get("identity_type", "ai"),
                        "id": data.get("id", ""),
                        "name": data.get("name", ""),
                        "role": data.get("role", "ai_agent"),
                    }
                    if result["verified"]:
                        self._verify_cache[agent_id] = (result, time.time())
                    return result
                return {"verified": False, "error": "Verification failed"}
        except httpx.TimeoutException:
            return {"verified": False, "error": "Verification timed out"}
        except Exception:
            return {"verified": False, "error": "Verification service unavailable"}

    async def intercept_request(self, request_context: dict) -> dict:
        agent_id = request_context.get("headers", {}).get("X-Agent-ID", "")
        if not agent_id:
            agent_id = request_context.get("metadata", {}).get("agent_id", "")
        if not agent_id:
            if self.reject_unverified:
                return {"allowed": False, "error": "No AI identity provided"}
            return {"allowed": True, "identity": None}
        identity = await self.verify_identity(agent_id)
        if not identity.get("verified"):
            if self.reject_unverified:
                return {"allowed": False, "error": "Invalid AI identity"}
            return {"allowed": True, "identity": None, "warning": "Invalid identity"}
        return {"allowed": True, "identity": identity}

    def wrap_server(self, server: Any) -> Any:
        server._anexus_middleware = self
        original_process = getattr(server, "process_request", None)

        async def wrapped_process(request):
            context = {
                "headers": getattr(request, "headers", {}),
                "metadata": getattr(request, "metadata", {}),
            }
            result = await self.intercept_request(context)
            if not result.get("allowed"):
                raise PermissionError(result.get("error", "Identity verification failed"))
            if result.get("identity"):
                request.ai_identity = result["identity"]
            if original_process:
                return await original_process(request)
            return request

        server.process_request = wrapped_process
        return server