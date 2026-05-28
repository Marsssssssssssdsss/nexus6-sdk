# Anexus Identity — MCP Server

Verify any AI Agent's identity. One command, any MCP-compatible client.

## For AI Assistants (Claude Code, Codex, Cursor)

Add to your MCP config file:

```json
{
  "mcpServers": {
    "anexus": {
      "command": "python",
      "args": ["-m", "anexus_mcp.server"]
    }
  }
}
```

Then ask your AI:

> "Verify agent ID: nxs6_47dd35b83e80415d9e19af3bedcad2fb"

The AI calls our MCP tool → returns verified identity details.

Works with: **Claude Code**, **Codex**, **Cursor**, **Claude Desktop**, and any MCP-compatible client.

## For Developers (protect your API)

Add our middleware to auto-verify agents by their `X-Agent-ID` header:

```python
from anexus_sdk.middleware import AnexusMiddleware
app.add_middleware(AnexusMiddleware)
```

Requests with `X-Agent-ID` are verified automatically. Invalid IDs get 401.

## Register an Agent

```python
from anexus_sdk import AnexusClient

client = AnexusClient()
result = client.register("my-agent")
agent_id = result["api_key"]  # permanent identity token
```

Or via API:

```bash
curl https://nexus-7xp6n.ondigitalocean.app/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name":"my-agent"}'
```

Returns: `{"success": true, "api_key": "nxs6_xxxxxxxxx", "id": "ai_xxxxxxxx"}`

## How it works

```
Agent                MCP Client (Claude Code/Codex)     Anexus Backend
  │                          │                                │
  │── X-Agent-ID ──────────►│                                │
  │                          │── verify_identity(agent_id) ──►│
  │                          │◄── {verified, id, name} ──────│
  │                          │                                │
  │                          │  (or automatically via middleware)
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

## SDK Docs

- [Python SDK](python/README.md) — client + FastAPI middleware
- [JavaScript SDK](javascript/README.md) — client + Express middleware

## License

MIT