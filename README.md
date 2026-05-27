# Anexus — AI Identity Infrastructure

<p align="center">
  <strong>Every AI Agent needs a verifiable identity. No unauthenticated AI call should be allowed.</strong><br>
  1-line middleware. HMAC signature verification. One-time agent_secret.
</p>

<p align="center">
  <a href="https://github.com/Marsssssssssssdsss/nexus6-sdk/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
</p>

---

## What is Anexus?

**MCP answers "what can this AI do?" — Anexus answers "who is this AI?"**

Anexus provides a universal identity verification layer for AI Agents. Any platform (MCP Server, API gateway, SaaS) can verify an AI Agent's identity with 1 line of middleware.

```
┌──────────────────────────────────────────────────────────────┐
│                   HMAC Signature Flow                        │
│                                                              │
│  AI Agent              Platform/MCP Server                   │
│     │                            │                           │
│     │── register()              │                           │
│     │   → api_key + agent_secret│                           │
│     │                            │                           │
│     │── sign request ──────────▶│                           │
│     │   X-API-Key: nxs6_xxx     │                           │
│     │   X-Agent-Signature       │                           │
│     │   X-Agent-Timestamp       │                           │
│     │                            │  fetch agent_secret      │
│     │                            │  (cached 1 hour)         │
│     │                            │                           │
│     │                            │  recompute HMAC-SHA256    │
│     │                            │  compare signatures       │
│     │                            │                           │
│     │◀── "Request allowed" ──────│                           │
└──────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Python (1-line middleware for platform)

```bash
pip install git+https://github.com/Marsssssssssssdsss/nexus6-sdk.git#subdirectory=python
```

```python
from anexus_sdk.middleware import AnexusMiddleware
app.add_middleware(AnexusMiddleware)
```

Every request with `X-API-Key` + signature headers is automatically verified.

### Signing requests (AI Agent side)

```python
from anexus_sdk import AnexusClient

client = AnexusClient()
result = client.register(name="My Agent")
api_key = result["api_key"]          # nxs6_xxx
agent_secret = result["agent_secret"] # as_xxx — save it, shown once

headers = client.build_auth_headers(
    agent_secret, "GET", "/api/v1/tools"
)
headers["X-API-Key"] = api_key
```

### One-time registration

```bash
pip install git+https://github.com/Marsssssssssssdsss/nexus6-sdk.git#subdirectory=python
python -c "
from anexus_sdk import AnexusClient
r = AnexusClient().register(name='my-agent')
print('api_key:', r['api_key'])
print('agent_secret:', r['agent_secret'])
"
```

### Direct HTTP API (any language)

```
POST https://nexus-7xp6n.ondigitalocean.app/api/v1/agents/register
{ "name": "my-agent" }
→ { "success": true, "api_key": "nxs6_xxx", "agent_secret": "as_xxx" }

POST https://nexus-7xp6n.ondigitalocean.app/api/v1/identity/verify
{
  "api_key": "nxs6_xxx",
  "signature": "hex...",
  "timestamp": 1700000000,
  "method": "GET",
  "path": "/api/v1/tools"
}
→ { "verified": true, "name": "My Agent" }
```

---

## How It Works

| Component | Purpose |
|-----------|---------|
| **API Key** (`nxs6_xxx`) | Identifies the agent (sent as `X-API-Key` header) |
| **Agent Secret** (`as_xxx`) | Signs requests via HMAC-SHA256 (shown once on registration) |

The middleware fetches the agent's secret from Anexus (cached for 1 hour), recomputes the HMAC, and compares. No asymmetric crypto, no key management.

---

## Relationship with MCP

| | Anexus | MCP |
|---|---|---|
| **Problem** | Identity & trust | Tool & resource access |
| **Question** | "Who are you?" | "What can you do?" |
| **Method** | HMAC-SHA256 signature | Custom server + client |
| **Integration** | 1-line middleware | Define tools, handle calls |

> **Best used together.** Anexus verifies AI identity at the gateway layer; MCP handles tool invocation once trust is established.

---

## Status

| Component | Status |
|-----------|--------|
| Identity API | ✅ Live (nexus-7xp6n.ondigitalocean.app) |
| Python SDK | ✅ `pip install anexus-sdk` |
| FastAPI Middleware | ✅ 1-line integration |
| Registration | ✅ One-time, returns api_key + agent_secret |

---

## Links

- **Live API:** https://nexus-7xp6n.ondigitalocean.app
- **GitHub:** https://github.com/Marsssssssssssdsss/nexus6-sdk
- **License:** MIT