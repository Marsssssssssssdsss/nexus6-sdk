"""Generate an auth verification code for your AI to access a platform.
For end users and AI agents. Platform developers use anexus_verify instead.

Usage (CLI):
    python -m anexus_sdk.code_gen --target shopify
    python -m anexus_sdk login         # Login first
    python -m anexus_sdk whoami        # Check login status

Usage (SDK — for AI agents):
    from anexus_sdk import generate_code, check_login

    # Before generating a code, check if logged in:
    status = check_login()
    if not status["logged_in"]:
        print("Please login first")
        return

    result = generate_code("shopify")
    code = result["code"]  # anx://shopify/user_xxx?exp=3600&ts=xxx

Reads session token from ~/.anexus/token (saved by `login.py`).
"""

import sys, os, json
from urllib.request import Request, urlopen
from urllib.error import URLError
from typing import Optional

TOKEN_PATH = os.path.expanduser("~/.anexus/token")
BASE_URL = os.environ.get("ANEXUS_BASE_URL", "https://nexus-7xp6n.ondigitalocean.app")


def _read_token(session_token: Optional[str] = None) -> Optional[str]:
    """Read session token from param or file. Returns None if missing."""
    if session_token:
        return session_token
    if not os.path.exists(TOKEN_PATH):
        return None
    with open(TOKEN_PATH) as f:
        token = f.read().strip()
    return token if token else None


def check_login(
    session_token: Optional[str] = None,
    base_url: Optional[str] = None,
) -> dict:
    """Check if the current session is still valid.

    AI agents should call this before generate_code() to verify
    the human has an active session:
        status = check_login()
        if status["logged_in"]:
            print(f"Logged in as {status['username']}")

    Returns:
        dict with keys: logged_in (bool), plus user info if logged in,
        or error message if not.
    """
    token = _read_token(session_token)
    if not token:
        return {"logged_in": False, "error": "Not logged in. Run `python -m anexus_sdk login` first."}

    url = (base_url or BASE_URL).rstrip("/")
    req = Request(
        f"{url}/api/v1/session/check",
        headers={"x-session-token": token},
    )

    try:
        with urlopen(req) as resp:
            data = json.loads(resp.read())
        return data
    except URLError as e:
        return {"logged_in": False, "error": f"Network error: {e.reason}"}
    except json.JSONDecodeError:
        return {"logged_in": False, "error": "Invalid response from server"}


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

    token = _read_token(session_token)
    if not token:
        return {
            "success": False,
            "error": "No session token found. Run `python -m anexus_sdk login` first.",
        }

    url = (base_url or BASE_URL).rstrip("/")
    payload = json.dumps({"target": target.strip().lower()}).encode()
    req = Request(
        f"{url}/api/v1/codes/generate",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-session-token": token,
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