"""Verify an Anexus auth code received from a user's AI agent.

This is the ONLY thing a platform developer needs:
  1. User's AI sends you a code like "anx://shopify/user_xxx?exp=3600&ts=..."
  2. You call verify_code() with your API Key
  3. If verified, you know exactly who the user is

You NEVER need generate_code() or login. That's the user's side.
"""

import json
import os
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

BASE_URL = os.environ.get("ANEXUS_BASE_URL", "http://localhost:8000")


def verify_code(
    code: str,
    api_key: str,
    api_secret: Optional[str] = None,
    base_url: Optional[str] = None,
) -> dict:
    """Verify an auth code received from a user's AI agent.

    Called by platform developers when a user's AI presents
    an Anexus auth code. Returns the user's verified identity.

    Args:
        code: The auth code from the AI, e.g. "anx://shopify/user_xxx?exp=3600&ts=..."
        api_key: Your platform's API Key from the Anexus Dashboard
        api_secret: Optional secret for HMAC-signed requests (extra security)
        base_url: API base URL. Falls back to ANEXUS_BASE_URL env or default.

    Returns:
        dict with keys: verified (bool), username, user_id, target_platform, etc.

    Example:
        result = verify_code(
            code="anx://shopify/user_xxx?exp=3600&ts=...",
            api_key="nxs6_xxxxxxxxxxxx",
        )
        if result["verified"]:
            grant_access(result["username"], result["target_platform"])
    """
    if not code:
        return {"verified": False, "error": "Auth code is required"}
    if not api_key:
        return {"verified": False, "error": "API Key is required. Get one from your Dashboard."}

    url = (base_url or BASE_URL).rstrip("/")
    payload = {"code": code, "api_key": api_key}

    if api_secret:
        import hashlib
        import hmac
        import time
        timestamp = str(int(time.time()))
        message = f"POST:/api/v1/codes/verify:{timestamp}"
        signature = hmac.new(
            api_secret.encode(), message.encode(), hashlib.sha256
        ).hexdigest()
        payload["timestamp"] = timestamp
        payload["signature"] = signature

    req = Request(
        f"{url}/api/v1/codes/verify",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )

    try:
        with urlopen(req) as resp:
            data = json.loads(resp.read())
        return data
    except URLError as e:
        if hasattr(e, "code") and e.code:
            try:
                err_data = json.loads(e.read())
                return err_data
            except Exception:
                pass
        return {"verified": False, "error": f"HTTP error: {e.reason}"}
    except json.JSONDecodeError:
        return {"verified": False, "error": "Invalid response from server"}