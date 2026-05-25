"""
nexus6_sdk — Nexus6 AI Identity SDK for Python.

One SDK for both roles in the AI identity ecosystem:

  Caller (AI Agent):
      sign_request(private_key, "POST:/api/v1/tools:1730000000")
      → returns RSA signature to send as X-Agent-Signature header

  Verifier (Platform):
      add_middleware(Nexus6Middleware)
      → drops into any FastAPI app, verifies every incoming request

Usage:
    from nexus6_sdk import Nexus6Client
    from nexus6_sdk.middleware import Nexus6Middleware
"""

__version__ = "0.2.0"
__author__ = "Nexus6"
__license__ = "MIT"

from .client import Nexus6Client
from .middleware import Nexus6Middleware

__all__ = ["Nexus6Client", "Nexus6Middleware"]
