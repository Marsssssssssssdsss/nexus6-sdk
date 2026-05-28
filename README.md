# Anexus

AI Agent identity. One header, one line.

## For Agent Developers

Register your agent once. Get a permanent identity token. Every service that uses Anexus will recognize it automatically.

```python
from anexus_sdk import AnexusClient

client = AnexusClient()
result = client.register("my-agent")
agent_id = result["api_key"]  # nxs6_xxxxxxxxx
```

Then send it as a header:

```
X-Agent-ID: nxs6_xxxxxxxxx
```

## For Service Providers

Add one line of middleware. Every incoming request with a valid `X-Agent-ID` is automatically verified. Invalid identities get 401.

```python
from anexus_sdk.middleware import AnexusMiddleware
app.add_middleware(AnexusMiddleware)
```

That's it. No OAuth setup. No login pages. Just verify AI agents by their identity.

## How it works

```
Agent                          Your MCP Server
  │                                  │
  │── X-Agent-ID header ────────────►│
  │                                  ├── verify with Anexus backend
  │                                  │── verified → allow
  │                                  │── invalid → 401
  │◄── response ────────────────────│
```

## Quick Start

```bash
pip install git+https://github.com/Marsssssssssssdsss/nexus6-sdk.git#subdirectory=python
```

```python
from anexus_sdk import AnexusClient

client = AnexusClient()
result = client.register("demo-agent")
print(result["api_key"])
```

## Docs

- [Python SDK](python/README.md) — client + FastAPI middleware
- [JavaScript SDK](javascript/README.md) — client + Express middleware

## License

MIT