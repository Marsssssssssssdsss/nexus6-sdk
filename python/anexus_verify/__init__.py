"""anexus_verify — Verify Anexus auth codes from users' AI agents.

For platform developers:
    from anexus_verify import verify_code

    result = verify_code(
        code="anx://shopify/user_xxx?exp=3600&ts=...",
        api_key="nxs6_xxxxxxxxxxxx",
    )
    if result["verified"]:
        grant_access(result["username"], result["target_platform"])
"""

__version__ = "0.1.0"
__author__ = "Anexus"
__license__ = "MIT"

from .verifier import verify_code

__all__ = ["verify_code"]