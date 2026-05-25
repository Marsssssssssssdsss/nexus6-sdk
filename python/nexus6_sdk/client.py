"""Nexus6 Client — AI identity registration and verification via RSA signature."""

import httpx
import time
from typing import Optional, Dict, Any

try:
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

import base64

DEFAULT_BASE_URL = "https://nexus-7xp6n.ondigitalocean.app"


class Nexus6Client:
    """Client for Nexus6 AI Identity system.

    Verification uses RSA signature: the api_key identifies the agent,
    the private key signs requests, and the platform verifies with the
    public key.

    Usage:
        # Register a new identity
        result = client.register(name="My AI Agent")
        # result contains api_key, private_key, public_key

        # Sign and verify
        headers = client.build_auth_headers(private_key, "GET", "/api/data")
        headers["X-API-Key"] = api_key

        # Verify a signature
        identity = client.verify(api_key, signature, timestamp, "GET", "/api/data")
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = DEFAULT_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def verify(self, api_key: Optional[str] = None, signature: Optional[str] = None,
               timestamp: Optional[str] = None, method: str = "POST",
               path: str = "/api/v1/identity/verify") -> Dict[str, Any]:
        """Verify an AI identity via RSA signature.

        Args:
            api_key: The agent's API key (identifier)
            signature: Base64 RSA signature of "METHOD:/path:timestamp"
            timestamp: Unix timestamp when the signature was created
            method: HTTP method that was signed
            path: Request path that was signed

        Returns:
            {"verified": True, "id": "ai_xxx", "name": "...", ...}
            or {"verified": False, "error": "...", "details": "..."}
        """
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
                    "error": "invalid_key",
                    "details": result.get("error", "API key rejected")
                }
        except httpx.TimeoutException:
            return {"verified": False, "error": "timeout", "details": "Verification request timed out"}
        except httpx.HTTPStatusError as e:
            return {"verified": False, "error": "server_error", "details": f"Server returned {e.response.status_code}"}
        except Exception as e:
            return {"verified": False, "error": "network_error", "details": str(e)}

    def register(self, name: str, **kwargs) -> Dict[str, Any]:
        """Register a new AI identity.

        Args:
            name: AI agent name
            **kwargs: optional fields (title, description, developer_email, etc.)

        Returns:
            {"success": True, "agent_id": "...", "api_key": "nxs6_xxx",
             "private_key": "...", "public_key": "..."}
            Store private_key securely — it can never be retrieved again.
        """
        payload = {"name": name, **kwargs}
        try:
            with httpx.Client(timeout=10) as http:
                resp = http.post(
                    f"{self.base_url}/api/ai/register",
                    json=payload
                )
                result = resp.json()
                if result.get("success") and "api_key" in result:
                    self.api_key = result["api_key"]
                return result
        except Exception as e:
            return {"success": False, "error": f"Registration failed: {str(e)}"}

    def create_token(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Create a one-time identity token (expires in 5 min).

        Returns:
            {"token": "idt_xxx", "expires_in": 300, "usage": "single-use"}
        """
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

    def fetch_public_key(self, ai_id: str) -> Optional[str]:
        """Fetch the public key for an AI agent by agent ID.

        Returns:
            PEM-encoded RSA public key string, or None if not found.
        """
        try:
            with httpx.Client(timeout=10) as http:
                resp = http.get(
                    f"{self.base_url}/api/v1/ai/keys/{ai_id}"
                )
                data = resp.json()
                if data.get("success") and data.get("public_key"):
                    return data["public_key"]
                return None
        except Exception:
            return None

    def fetch_public_key_by_api_key(self, api_key: Optional[str] = None) -> Optional[str]:
        """Fetch the public key by API key. Used by middleware for offline verification.

        Returns:
            PEM-encoded RSA public key string, or None if not found.
        """
        key = api_key or self.api_key
        if not key:
            return None
        try:
            with httpx.Client(timeout=10) as http:
                resp = http.get(
                    f"{self.base_url}/api/v1/keys/public",
                    params={"api_key": key}
                )
                data = resp.json()
                if data.get("success") and data.get("public_key"):
                    return data["public_key"]
                return None
        except Exception:
            return None

    def generate_keys(self, ai_id: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Generate RSA key pair and upload public key to Nexus6.

        Args:
            ai_id: AI agent ID (e.g. "ai_xxxxxxxx")
            api_key: API key for authentication

        Returns:
            {"success": True, "ai_id": "...", "public_key": "...", "private_key": "..."}
            Store private_key securely — it cannot be retrieved later.
        """
        key = api_key or self.api_key
        if not key:
            return {"success": False, "error": "No API key provided"}

        if not CRYPTO_AVAILABLE:
            return {"success": False, "error": "cryptography package required: pip install cryptography"}

        try:
            private_key_obj = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )

            private_pem = private_key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()

            public_pem = private_key_obj.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()

            with httpx.Client(timeout=10) as http:
                resp = http.post(
                    f"{self.base_url}/api/v1/ai/keys/generate",
                    json={"ai_id": ai_id, "public_key": public_pem},
                    headers={"X-API-Key": key}
                )
                data = resp.json()

            if data.get("success"):
                return {
                    "success": True,
                    "ai_id": ai_id,
                    "public_key": public_pem,
                    "private_key": private_pem,
                    "message": "Store the private key securely — it cannot be retrieved later."
                }
            return data
        except Exception as e:
            return {"success": False, "error": f"Key generation failed: {str(e)}"}

    def sign_request(self, private_key_pem: str, message: str) -> str:
        """Sign a message with the agent's private key.

        Args:
            private_key_pem: PEM-encoded RSA private key
            message: Message to sign (e.g. "POST:/api/v1/tools:1700000000")

        Returns:
            Base64-encoded RSA signature string.
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography package required: pip install cryptography")

        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )

        signature = private_key.sign(
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode()

    def build_auth_headers(self, private_key_pem: str, method: str = "GET", path: str = "/") -> Dict[str, str]:
        """Build authentication headers for an HTTP request.

        The API key must be sent separately as X-API-Key header.

        Args:
            private_key_pem: PEM-encoded RSA private key
            method: HTTP method (GET, POST, etc.)
            path: Request path

        Returns:
            Dict with X-Agent-Signature and X-Agent-Timestamp headers.
        """
        timestamp = str(int(time.time()))
        message = f"{method}:{path}:{timestamp}"
        signature = self.sign_request(private_key_pem, message)

        return {
            "X-Agent-Signature": signature,
            "X-Agent-Timestamp": timestamp,
        }

    def verify_signature_offline(self, public_key_pem: str, message: str, signature_b64: str) -> bool:
        """Verify an RSA signature locally — no network call required.

        Args:
            public_key_pem: PEM-encoded RSA public key
            message: Original message that was signed
            signature_b64: Base64-encoded RSA signature

        Returns:
            True if signature is valid, False otherwise.
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography package required: pip install cryptography")

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