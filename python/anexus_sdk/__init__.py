"""
anexus_sdk — Anexus Auth Codes SDK for Python.

For humans:
    python -m anexus_sdk login          # Browser login (GitHub Copilot style)
    python -m anexus_sdk code shopify   # Generate verification code

For AI agents (programmatic):
    from anexus_sdk import generate_code

    # After human has logged in via CLI:
    result = generate_code("shopify")
    code = result["code"]
    # -> "anx://shopify/user_xxx?exp=3600&ts=xxx"
    # Use this code to call the target platform's API / MCP server.

For platform developers:
    from anexus_sdk.middleware import AnexusMiddleware
    from anexus_sdk import AnexusClient
"""

__version__ = "0.3.0"
__author__ = "Anexus"
__license__ = "MIT"

from .client import AnexusClient
from .middleware import AnexusMiddleware
from .identity_store import IdentityStore
from .code_gen import generate_code

__all__ = [
    "AnexusClient",
    "AnexusMiddleware",
    "IdentityStore",
    "generate_code",
]