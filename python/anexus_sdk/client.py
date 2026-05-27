"""Anexus Client — register an AI identity and get a permanent token."""

import httpx
from typing import Optional, Dict, Any

DEFAULT_BASE_URL = "https://nexus-7xp6n.ondigitalocean.app"


class AnexusClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.agent_id: Optional[str] = None

    def register(self, name: str, **kwargs) -> Dict[str, Any]:
        if not name or not name.strip():
            return {"success": False, "error": "Agent name is required"}
        payload = {"name": name.strip(), **kwargs}
        try:
            with httpx.Client(timeout=10) as http:
                resp = http.post(f"{self.base_url}/api/v1/agents/register", json=payload)
                result = resp.json()
                if result.get("success"):
                    self.agent_id = result.get("api_key")
                return result
        except httpx.TimeoutException:
            return {"success": False, "error": "Registration timed out"}
        except Exception as e:
            return {"success": False, "error": f"Registration failed: {str(e)}"}

    def verify(self, agent_id: str) -> Dict[str, Any]:
        if not agent_id:
            return {"verified": False, "error": "Agent ID is required"}
        try:
            with httpx.Client(timeout=10) as http:
                resp = http.post(
                    f"{self.base_url}/api/v1/identity/verify",
                    json={"api_key": agent_id}
                )
                result = resp.json()
                if resp.status_code == 200 and result.get("verified"):
                    return {
                        "verified": True,
                        "identity_type": result.get("identity_type", "ai"),
                        "id": result["id"],
                        "name": result.get("name", result["id"]),
                        "role": result.get("role", "ai_agent"),
                    }
                return {"verified": False, "error": result.get("error", "invalid_key")}
        except httpx.TimeoutException:
            return {"verified": False, "error": "Verification timed out"}
        except Exception as e:
            return {"verified": False, "error": f"Verification failed: {str(e)}"}