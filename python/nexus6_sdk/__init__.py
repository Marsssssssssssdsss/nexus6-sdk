"""
nexus6_sdk — Nexus6 AI Identity SDK for Python.

5-minute integration for AI agents and platforms.

Usage:
    # AI Agent side
    from nexus6_sdk import Nexus6Client
    client = Nexus6Client(api_key="nxs6_xxx")
    identity = client.verify()

    # Platform side (FastAPI middleware)
    from nexus6_sdk.middleware import Nexus6Middleware
    app.add_middleware(Nexus6Middleware, api_key="nxs6_xxx")
"""

__version__ = "0.1.0"
__author__ = "Nexus6"
__license__ = "MIT"

from .client import Nexus6Client
from .middleware import Nexus6Middleware

__all__ = ["Nexus6Client", "Nexus6Middleware"]
