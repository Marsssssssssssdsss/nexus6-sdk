"""Anexus Client — AI identity registration and request signing."""

import httpx
import time
import hmac
import hashlib
from typing import Optional, Dict, Any

DEFAULT_BASE_URL = "https://nexus-7xp6n.ondigitalocean.app"


class AnexusClient:
    def __init__(self, api_key: Optional[str] = None, agent_secret: Optional[str] = None, base_url: str = DEFAULT_BASE_URL):
        self.api_key = api_key
        self.agent_secret = agent_secret
        self.base_url = base_url.rstrip("/")

    def register(self, name: str, **kwargs) -> Dict[str, Any]:
        payload = {"name": name, **kwargs}
        try:
            with httpx.Client(timeout=10) as http:
                resp = http.post(
                    f"{self.base_url}/api/v1/agents/register",
                    json=payload
                )
                result = resp.json()
                if result.get("success"):
                    self.api_key = result.get("api_key")
                    self.agent_secret = result.get("agent_secret")
                return result
        except Exception as e:
            return {"success": False, "error": f"Registration failed: {str(e)}"}

    def sign_request(self, agent_secret: str, method: str, path: str, timestamp: str) -> str:
        message = f"{method}:{path}:{timestamp}"
        return hmac.new(agent_secret.encode(), message.encode(), hashlib.sha256).hexdigest()

    def build_auth_headers(self, agent_secret: str, method: str = "GET", path: str = "/") -> Dict[str, str]:
        timestamp = str(int(time.time()))
        signature = self.sign_request(agent_secret, method, path, timestamp)
        return {
            "X-Agent-Signature": signature,
            "X-Agent-Timestamp": timestamp,
        }

    def verify(self, api_key: Optional[str] = None, signature: Optional[str] = None,
               timestamp: Optional[str] = None, method: str = "POST",
               path: str = "/api/v1/identity/verify") -> Dict[str, Any]:
        key = api_key or self.api_key
        if not key:
            return {"verified": False, "error": "no_api_key", "details": "Provide api_key or set it in client."}
        try:
            body = {"api_key": key}
            if signature and timestamp:
                body["signature"] = signature
                body["timestamp"] = timestamp
                body["method"] = method
                body["path"] = path
            with httpx.Client(timeout=10) as http:
                resp = http.post(
                    f"{self.base_url}/api/v1/identity/verify",
                    json=body
                )
                result = resp.json()
                if resp.status_code == 200 and result.get("verified"):
                    return {
                        "verified": True,
                        "identity_type": result.get("identity_type", "ai"),
                        "id": result["id"],
                        "name": result.get("name", result["id"]),
                        "role": result.get("role", "ai_agent"),
                        "ai_type": result.get("ai_type", "general"),
                    }
                return {
                    "verified": False,
                    "error": result.get("error", "invalid_key"),
                    "details": result.get("details", "API key rejected")
                }
        except httpx.TimeoutException:
            return {"verified": False, "error": "timeout", "details": "Verification request timed out"}
        except httpx.HTTPStatusError as e:
            return {"verified": False, "error": "server_error", "details": f"Server returned {e.response.status_code}"}
        except Exception as e:
            return {"verified": False, "error": "network_error", "details": str(e)}

    def create_token(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        key = api_key or self.api_key
        if not key:
            return {"error": "No API key provided"}
        try:
            with httpx.Client(timeout=10) as http:
                resp = http.post(
                    f"{self.base_url}/api/v1/identity/token",
                    headers={"X-API-Key": key}
                )
                return resp.json()
        except Exception as e:
            return {"error": f"Token creation failed: {str(e)}"}