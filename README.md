# Anexus — AI Identity Infrastructure

<p align="center">
  <strong>Every AI Agent needs a verifiable identity. No unauthenticated AI call should be allowed.</strong><br>
  1-line middleware. RSA signature verification. API key as identifier.
</p>

<p align="center">
  <a href="https://pypi.org/project/anexus-sdk/"><img src="https://img.shields.io/pypi/v/anexus-sdk?color=blue" alt="PyPI"></a>
  <a href="https://github.com/Marsssssssssssdsss/nexus6-sdk/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
  <a href="https://pypi.org/project/anexus-sdk/"><img src="https://img.shields.io/pypi/pyversions/anexus-sdk" alt="Python"></a>
</p>

---

## What is Anexus?

**MCP answers "what can this AI do?" — Anexus answers "who is this AI?"**

Anexus provides a universal identity verification layer for AI Agents. Any platform (MCP Server, API gateway, SaaS) can verify an AI Agent's identity with 1 line of middleware.

```
┌─────────────────────────────────────────────────────────────┐
│                   RSA Signature Flow                         │
│                                                              │
│  AI Agent              Anexus Platform         MCP Server    │
│     │                        │                      │        │
│     │── register() ────────▶│                      │        │
│     │◀── api_key ───────────│                      │        │
│     │    + private_key      │                      │        │
│     │                        │                      │        │
│     │── sign(request) ────────────────────────────▶│        │
│     │   X-API-Key: nxs6_xxx  │                      │        │
│     │   X-Agent-Signature    │                      │        │
│     │   X-Agent-Timestamp    │                      │        │
│     │                        │  fetch public key    │        │
│     │                        │◀────────────────────│        │
│     │                        │── public_key ───────▶│        │
│     │                        │                      │        │
│     │                        │   verify signature   │        │
│     │                        │   locally (cached)   │        │
│     │◀────────────────────────── "Request allowed" ─│        │
└──────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Python (1-line middleware)

```bash
pip install anexus-sdk
```

```python
from anexus_sdk.middleware import AnexusMiddleware
app.add_middleware(AnexusMiddleware)
```

Every request with `X-API-Key` + signature headers is automatically verified.

### JavaScript (1-line middleware)

```bash
npm install github:Marsssssssssssdsss/anexus-sdk
```

```javascript
const { createAnexusMiddleware } = require('anexus-sdk/javascript');
app.use(createAnexusMiddleware());
```

### Signing requests (agent side)

```python
from anexus_sdk import AnexusClient
client = AnexusClient(api_key="nxs6_xxx")
headers = client.build_auth_headers(private_key, "GET", "/api/v1/tools")
headers["X-API-Key"] = api_key
```

```javascript
const { AnexusClient } = require('anexus-sdk');
const client = new AnexusClient({ apiKey: "nxs6_xxx" });
const headers = client.buildAuthHeaders(privateKey, "GET", "/api/v1/tools");
headers["X-API-Key"] = apiKey;
```

### Direct HTTP API (any language)

```
POST https://nexus-7xp6n.ondigitalocean.app/api/v1/identity/verify
{
  "api_key": "nxs6_xxx",
  "signature": "base64...",
  "timestamp": 1700000000,
  "method": "GET",
  "path": "/api/v1/tools"
}
→ { "verified": true, "id": "ai_xxx", "name": "MyAgent" }
```

---

## How It Works

Anexus uses a **unified identity system**:

| Component | Purpose |
|-----------|---------|
| **API Key** (`nxs6_xxx`) | Identifies the agent (sent as `X-API-Key` header) |
| **Private Key** | Signs requests (held securely by the agent) |
| **Public Key** | Verifies signatures (stored on Anexus, cached by middleware) |

Verification is done **locally by the middleware** using the cached public key — no network round-trip for every request.

---

## Relationship with MCP

| | Anexus | MCP |
|---|---|---|
| **Problem** | Identity & trust | Tool & resource access |
| **Question** | "Who are you?" | "What can you do?" |
| **Method** | RSA signature verification | Custom server + client |
| **Integration** | 1-line middleware | Define tools, handle calls |

> **Best used together.** Anexus verifies AI identity at the gateway layer; MCP handles tool invocation once trust is established.

---

## Repo Structure

```
anexus-sdk/
├── python/              # Python SDK (published to PyPI)
│   ├── anexus_sdk/
│   │   ├── __init__.py
│   │   ├── client.py        # Registration, verification, token
│   │   └── middleware.py    # FastAPI/Starlette middleware
│   ├── pyproject.toml
│   └── README.md
├── javascript/          # JavaScript SDK
│   ├── index.js             # Client + Express middleware
│   ├── package.json
│   └── README.md
├── anexus_mcp/          # MCP Server
│   └── server.py            # verify_identity + get_agent_info
├── LICENSE
└── README.md
```

---

## Status

| Component | Status |
|-----------|--------|
| Identity API | ✅ Live (nexus-7xp6n.ondigitalocean.app) |
| Python SDK | ✅ `pip install anexus-sdk` |
| JavaScript SDK | ✅ npm / GitHub direct install |
| FastAPI Middleware | ✅ 1-line integration |
| Express.js Middleware | ✅ 1-line integration |
| MCP Server | ✅ verify_identity tool |
| RSA Offline Verification | ✅ 2048-bit, local signature verification |

---

## Links

- **Live API:** https://nexus-7xp6n.ondigitalocean.app
- **PyPI:** https://pypi.org/project/anexus-sdk/
- **License:** MIT