"""
anexus_sdk — Anexus AI Identity SDK for Python.

One SDK for both roles in the AI identity ecosystem:

  Caller (AI Agent):
      build_auth_headers(agent_secret, "POST", "/api/v1/tools")
      → returns X-Agent-Signature + X-Agent-Timestamp headers

  Verifier (Platform):
      add_middleware(AnexusMiddleware)
      → drops into any FastAPI app, verifies every incoming request

Usage:
    from anexus_sdk import AnexusClient
    from anexus_sdk.middleware import AnexusMiddleware
"""

__version__ = "0.2.0"
__author__ = "Anexus"
__license__ = "MIT"

from .client import AnexusClient
from .middleware import AnexusMiddleware

__all__ = ["AnexusClient", "AnexusMiddleware"]