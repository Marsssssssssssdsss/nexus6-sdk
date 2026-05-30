"""Anexus Client — AI identity lifecycle management."""

import httpx
from typing import Optional, Dict, Any
from .identity_store import IdentityStore

DEFAULT_BASE_URL = "https://nexus-7xp6n.ondigitalocean.app"


class AnexusClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        identity_store: Optional[IdentityStore] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.agent_id: Optional[str] = None
        self.agent_name: Optional[str] = None
        self._store = identity_store or IdentityStore()
        self._identity_data: dict = {}
        self._restore()

    def _restore(self):
        saved = self._store.load()
        if saved:
            self.agent_id = saved.get("api_key") or saved.get("agent_id")
            self.agent_name = saved.get("name")
            self._identity_data = saved

    def _persist(self, data: dict):
        self._identity_data = data
        self._store.save(data)

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
                    self.agent_name = name.strip()
                    self._persist({
                        "api_key": self.agent_id,
                        "name": self.agent_name,
                        "agent_id": result.get("agent_id", ""),
                    })
                return result
        except httpx.TimeoutException:
            return {"success": False, "error": "Registration timed out"}
        except Exception as e:
            return {"success": False, "error": f"Registration failed: {str(e)}"}

    def auth(self, name: str = "My AI Agent") -> Dict[str, Any]:
        """Start Device Authorization Flow.
        Prints a code and URL for the human to authorize in their browser.
        Polls until authorized or expired."""
        try:
            with httpx.Client(timeout=10) as http:
                resp = http.post(f"{self.base_url}/api/v1/device/authorize", json={"name": name.strip()})
                result = resp.json()
        except Exception as e:
            return {"success": False, "error": f"Authorization request failed: {str(e)}"}

        if not result.get("success"):
            return result

        device_code = result["device_code"]
        user_code = result["user_code"]
        verification_uri = result["verification_uri"]

        print()
        print("=" * 56)
        print("  Anexus Device Authorization")
        print("=" * 56)
        print()
        print(f"  1. Open your browser and go to:")
        print(f"     {verification_uri}")
        print()
        print(f"  2. Enter the authorization code:")
        print(f"     \033[1;36m{user_code}\033[0m")
        print()
        print(f"  3. Log in and authorize your AI Agent")
        print()
        print(f"  Code expires in {result.get('expires_in', 600)} seconds")
        print("=" * 56)
        print()

        import time
        poll_interval = 5
        max_attempts = 120
        for attempt in range(max_attempts):
            time.sleep(poll_interval)
            try:
                with httpx.Client(timeout=10) as http:
                    poll_resp = http.post(f"{self.base_url}/api/v1/device/poll", json={"device_code": device_code})
                    poll_result = poll_resp.json()
            except Exception:
                continue

            if poll_result.get("status") == "authorized":
                data = poll_result
                self.agent_id = data.get("api_key")
                self.agent_name = name.strip()
                self._persist({
                    "api_key": self.agent_id,
                    "name": self.agent_name,
                    "agent_id": data.get("agent_id", ""),
                    "agent_secret": data.get("agent_secret", ""),
                })
                print(f"\n  \033[1;32mAuthorized! API Key: {self.agent_id}\033[0m\n")
                return {"success": True, "api_key": self.agent_id, "agent_id": data.get("agent_id"), "agent_secret": data.get("agent_secret")}

            if poll_result.get("status") == "expired":
                return {"success": False, "error": "Authorization timed out. Please try again."}

        return {"success": False, "error": "Polling timed out."}

    def identify(self) -> Optional[Dict[str, Any]]:
        if not self.agent_id:
            self._restore()
        if not self.agent_id:
            return None
        return {
            "agent_id": self.agent_id,
            "name": self.agent_name or "",
            "is_identified": True,
        }

    def get_identity(self) -> Optional[Dict[str, Any]]:
        if not self.agent_id:
            self._restore()
        if not self.agent_id:
            return None
        result = self.verify(self.agent_id)
        if result.get("verified"):
            result["agent_id"] = self.agent_id
        return result

    def claim(self, endpoint: str, data: dict = None, method: str = "POST") -> Dict[str, Any]:
        if not self.agent_id:
            return {"success": False, "error": "No identity. Call register() or identify() first."}

        headers = {
            "X-Agent-ID": self.agent_id,
            "Content-Type": "application/json",
        }
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}{endpoint}"

        try:
            with httpx.Client(timeout=30) as http:
                if method.upper() == "GET":
                    resp = http.get(url, headers=headers, params=data)
                else:
                    resp = http.request(method.upper(), url, headers=headers, json=data or {})
                return {
                    "success": resp.status_code < 400,
                    "status_code": resp.status_code,
                    "data": resp.json() if resp.text else {},
                }
        except httpx.TimeoutException:
            return {"success": False, "error": "Request timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def done(self) -> Dict[str, Any]:
        if not self.agent_id:
            return {"success": False, "error": "No identity to deregister"}
        try:
            with httpx.Client(timeout=10) as http:
                resp = http.post(
                    f"{self.base_url}/api/v1/agents/deregister",
                    json={"api_key": self.agent_id}
                )
                result = resp.json()
        except Exception:
            result = {"success": True}

        self._store.clear()
        self.agent_id = None
        self.agent_name = None
        self._identity_data = {}
        return result

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

    def discover_agents(self, query: str = None, ai_type: str = None, min_trust: int = 0) -> Dict[str, Any]:
        params = {}
        if query:
            params["query"] = query
        if ai_type:
            params["ai_type"] = ai_type
        if min_trust > 0:
            params["min_trust_score"] = min_trust

        try:
            with httpx.Client(timeout=10) as http:
                resp = http.get(f"{self.base_url}/api/v1/discover/agents", params=params)
                return resp.json()
        except Exception as e:
            return {"success": False, "error": str(e), "agents": []}

    def trust_agent(self, target_id: str, trust_level: int = 1) -> Dict[str, Any]:
        if not self.agent_id:
            return {"success": False, "error": "No identity. Call register() or identify() first."}
        try:
            with httpx.Client(timeout=10) as http:
                resp = http.post(
                    f"{self.base_url}/api/v1/agents/{self.agent_id}/trust/{target_id}",
                    json={"trust_level": trust_level},
                    headers={"X-Agent-ID": self.agent_id}
                )
                return resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_trust_network(self) -> Dict[str, Any]:
        if not self.agent_id:
            return {"success": False, "error": "No identity"}
        try:
            with httpx.Client(timeout=10) as http:
                resp = http.get(f"{self.base_url}/api/v1/agents/{self.agent_id}/trust")
                return resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}