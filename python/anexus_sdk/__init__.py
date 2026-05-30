"""
anexus_sdk — Anexus Auth Codes SDK for Python.

For humans:
    python -m anexus_sdk login          # Browser login (GitHub Copilot style)
    python -m anexus_sdk whoami         # Check login status
    python -m anexus_sdk code shopify   # Generate verification code

For AI agents (programmatic):
    from anexus_sdk import generate_code, check_login

    # First check if the human is still logged in:
    status = check_login()
    if not status["logged_in"]:
        print("Please login first")
        return

    # Then generate a verification code:
    result = generate_code("shopify")
    code = result["code"]
    # -> "anx://shopify/user_xxx?exp=3600&ts=xxx"

For platform developers:
    from anexus_sdk import AnexusClient
    from anexus_sdk.middleware import AnexusMiddleware
"""

__version__ = "0.3.0"
__author__ = "Anexus"
__license__ = "MIT"

from .client import AnexusClient
from .middleware import AnexusMiddleware
from .identity_store import IdentityStore
from .code_gen import generate_code, check_login

__all__ = [
    "AnexusClient",
    "AnexusMiddleware",
    "IdentityStore",
    "generate_code",
    "check_login",
]