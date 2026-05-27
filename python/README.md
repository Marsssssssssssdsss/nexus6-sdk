# Anexus Python SDK

## Server side (FastAPI)

```bash
pip install git+https://github.com/Marsssssssssssdsss/nexus6-sdk.git#subdirectory=python
```

```python
from anexus_sdk.middleware import AnexusMiddleware
app.add_middleware(AnexusMiddleware)
```

Requests without `X-Agent-ID` pass through. Requests with `X-Agent-ID` are verified automatically.

Access the verified identity in your handlers:

```python
@app.post("/api/v1/tools")
async def handle(request: Request):
    identity = request.state.ai_identity
    # {"verified": True, "id": "ai_xxx", "name": "my-agent"}
```

## Agent side (register once, use forever)

```python
from anexus_sdk import AnexusClient

client = AnexusClient()
result = client.register(name="My Agent")
agent_id = result["api_key"]  # nxs6_xxxxxxxxx
```

Then send `X-Agent-ID: nxs6_xxxxxxxxx` with every request.

## Configuration

```python
AnexusMiddleware(
    app,
    base_url="https://nexus-7xp6n.ondigitalocean.app",
    exclude_paths=["/health", "/docs"],
)
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/agents/register` | POST | Register a new agent → `{api_key}` |
| `/api/v1/identity/verify` | POST | Verify an agent's identity |

## License

MIT