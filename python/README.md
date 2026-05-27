# Anexus Python SDK

## Server side (FastAPI middleware)

```bash
pip install git+https://github.com/Marsssssssssssdsss/nexus6-sdk.git#subdirectory=python
```

```python
from anexus_sdk.middleware import AnexusMiddleware
app.add_middleware(AnexusMiddleware)
```

Requests without `X-API-Key` pass through. Requests with `X-API-Key` must have valid `X-Agent-Signature` and `X-Agent-Timestamp` headers.

Access the verified identity in your handlers:

```python
@app.post("/api/v1/tools")
async def handle(request: Request):
    identity = request.state.ai_identity
    # {"verified": True, "identity": {"api_key": "...", "verified_by": "hmac-signature"}}
```

## Agent side (signing requests)

```python
from anexus_sdk import AnexusClient

client = AnexusClient()
result = client.register(name="My Agent")
# result = {"api_key": "nxs6_xxx", "agent_secret": "as_xxx"}

headers = client.build_auth_headers("as_xxx", "GET", "/api/v1/tools")
headers["X-API-Key"] = "nxs6_xxx"
```

## Configuration

```python
AnexusMiddleware(
    app,
    base_url="https://nexus-7xp6n.ondigitalocean.app",
    exclude_paths=["/health", "/docs"],
    signature_max_age_seconds=300,
)
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/agents/register` | POST | Register a new agent → `{api_key, agent_secret}` |
| `/api/v1/identity/verify` | POST | Verify an agent's identity |
| `/api/v1/identity/token` | POST | Create a short-lived session token |

## License

MIT