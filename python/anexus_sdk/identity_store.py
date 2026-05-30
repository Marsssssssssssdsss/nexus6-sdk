"""Anexus Identity Store — persist and restore AI agent identity.

Stores identity to ~/.anexus/identity.json or custom path.
Falls back to ANEXUS_AGENT_ID environment variable.
"""

import json
import os
from typing import Optional, Dict, Any

DEFAULT_IDENTITY_DIR = os.path.expanduser("~/.anexus")
DEFAULT_IDENTITY_FILE = os.path.join(DEFAULT_IDENTITY_DIR, "identity.json")


class IdentityStore:
    def __init__(self, path: Optional[str] = None):
        self.path = path or os.environ.get("ANEXUS_IDENTITY_PATH") or DEFAULT_IDENTITY_FILE

    def save(self, identity: Dict[str, Any]):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        existing = self._read_existing()
        existing.update(identity)
        with open(self.path, "w") as f:
            json.dump(existing, f, indent=2)

    def load(self) -> Optional[Dict[str, Any]]:
        env_id = os.environ.get("ANEXUS_AGENT_ID")
        env_key = os.environ.get("ANEXUS_API_KEY")

        if env_id or env_key:
            result = {}
            if env_id:
                result["agent_id"] = env_id
            if env_key:
                result["api_key"] = env_key
            return result

        return self._read_existing() or None

    def clear(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def _read_existing(self) -> Dict[str, Any]:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}