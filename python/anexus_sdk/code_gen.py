"""Generate an auth verification code for your AI to access a platform.

Usage (CLI):
    python -m anexus_sdk.code_gen --target shopify

Usage (SDK — for AI agents):
    from anexus_sdk import generate_code
    result = generate_code("shopify")
    code = result["code"]  # anx://shopify/user_xxx?exp=3600&ts=xxx

Reads session token from ~/.anexus/token (saved by `login.py`).
"""

import sys, os, json
from urllib.request import Request, urlopen
from urllib.error import URLError
from typing import Optional

TOKEN_PATH = os.path.expanduser("~/.anexus/token")
BASE_URL = os.environ.get("ANEXUS_BASE_URL", "http://localhost:8000")


def generate_code(
    target: str,
    session_token: Optional[str] = None,
    base_url: Optional[str] = None,
) -> dict:
    """Request a verification code for the given target platform.

    Args:
        target: Platform name, e.g. 'shopify', 'notion'
        session_token: Session token. If None, reads from ~/.anexus/token
        base_url: API base URL. Falls back to ANEXUS_BASE_URL env or default.

    Returns:
        dict with keys: success, code, target, expires_in, geo_location

    AI agents should call this directly after login:
        code = generate_code("shopify")["code"]
    """
    if not target:
        return {"success": False, "error": "Target platform is required"}

    if not session_token:
        if not os.path.exists(TOKEN_PATH):
            return {
                "success": False,
                "error": "No session token found. Run `python -m anexus_sdk login` first.",
            }
        with open(TOKEN_PATH) as f:
            session_token = f.read().strip()

    if not session_token:
        return {"success": False, "error": "Empty session token. Please login again."}

    url = (base_url or BASE_URL).rstrip("/")
    payload = json.dumps({"target": target.strip().lower()}).encode()
    req = Request(
        f"{url}/api/v1/codes/generate",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-session-token": session_token,
        },
    )

    try:
        with urlopen(req) as resp:
            data = json.loads(resp.read())
    except URLError as e:
        return {"success": False, "error": f"Network error: {e.reason}"}
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid response from server"}

    return data


def main():
    target = None
    for i, a in enumerate(sys.argv[1:]):
        if a in ("-t", "--target") and i + 1 < len(sys.argv[1:]):
            target = sys.argv[i + 2]
        elif not a.startswith("-"):
            target = a

    if not target:
        print("Usage: python -m anexus_sdk.code_gen --target <platform>")
        print("  e.g. python -m anexus_sdk.code_gen --target shopify")
        sys.exit(1)

    result = generate_code(target)

    if not result.get("success"):
        print(f"Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)

    code = result["code"]
    target_fmt = result.get("target", target)
    expires = result.get("expires_in", "?")
    geo = result.get("geo_location", "")

    print("")
    print(f"  Verification Code for {target_fmt}")
    print(f"  {'=' * 35}")
    print(f"  {code}")
    print("")
    print(f"  Expires: {expires}{' | Location: ' + geo if geo else ''}")
    print("")
    print(f"  Give this code to your AI to call {target_fmt}.")
    print("")


if __name__ == "__main__":
    main()