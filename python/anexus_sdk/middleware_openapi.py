"""Anexus OpenAPI Middleware — inject identity verification into OpenAPI specs."""

from .middleware import AnexusMiddleware
from typing import Optional, List, Callable


DEFAULT_BASE_URL = "https://nexus-7xp6n.ondigitalocean.app"


class AnexusOpenAPIMiddleware(AnexusMiddleware):
    def __init__(
        self,
        app,
        base_url: str = DEFAULT_BASE_URL,
        exclude_paths: Optional[List[str]] = None,
        on_verified: Optional[Callable] = None,
        inject_spec: bool = True,
        security_scheme_name: str = "X-Agent-ID",
    ):
        super().__init__(
            app,
            base_url=base_url,
            exclude_paths=exclude_paths,
            on_verified=on_verified,
        )
        self.inject_spec = inject_spec
        self.security_scheme_name = security_scheme_name
        self._original_openapi = None

    async def dispatch(self, request, call_next):
        if self.inject_spec and request.url.path in ("/openapi.json", "/docs"):
            if hasattr(request.app, "openapi"):
                self._original_openapi = request.app.openapi
                request.app.openapi = self._patched_openapi
        return await super().dispatch(request, call_next)

    def _patched_openapi(self):
        if callable(self._original_openapi):
            spec = self._original_openapi()
        else:
            spec = getattr(self._original_openapi, "__dict__", {})
        if not isinstance(spec, dict):
            return spec
        if "components" not in spec:
            spec["components"] = {}
        if "securitySchemes" not in spec["components"]:
            spec["components"]["securitySchemes"] = {}

        spec["components"]["securitySchemes"][self.security_scheme_name] = {
            "type": "apiKey",
            "in": "header",
            "name": "X-Agent-ID",
            "description": "Anexus AI Agent Identity Token. Register at https://nexus-7xp6n.ondigitalocean.app",
        }

        if "security" not in spec:
            spec["security"] = []

        existing = any(
            self.security_scheme_name in s for s in spec["security"]
        )
        if not existing:
            spec["security"].append({self.security_scheme_name: []})

        return spec