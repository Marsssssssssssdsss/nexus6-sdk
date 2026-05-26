# Anexus Python SDK

One SDK for both sides of AI identity:

- **Caller** (AI Agent) — register an identity, sign every request with HMAC-SHA256
- **Verifier** (Platform) — drop in 1 line of middleware, verify every incoming request

Zero cryptography dependencies. Uses Python stdlib `hmac` + `hashlib`.

---

## Installation

```bash
pip install anexus-sdk
```

---

## Quick Start

### 1. Register an Identity

```python
from anexus_sdk import AnexusClient

client = AnexusClient()
result = client.register(name="My AI Agent")
api_key = result["api_key"]       # nxs6_xxxxxxxxx
agent_secret = result["agent_secret"]  # as_xxxxxxxxx — save this!
```

### 2. Sign Every Outgoing Request

```python
headers = client.build_auth_headers(agent_secret, "POST", "/api/v1/chat")
headers["X-API-Key"] = api_key
# → {
#     "X-API-Key": "nxs6_xxx",
#     "X-Agent-Signature": "abc123...",
#     "X-Agent-Timestamp": "1700000000"
# }
```

The signature is `HMAC-SHA256(agent_secret, "METHOD:/path:timestamp")`. Each signature is valid for 5 minutes and tied to one specific method + path.

### 3. Verify on the Platform Side (FastAPI)

```python
from anexus_sdk.middleware import AnexusMiddleware
app.add_middleware(AnexusMiddleware)

@app.post("/api/v1/chat")
async def chat(request: Request):
    identity = request.state.ai_identity
    # → {"verified": True, "identity": {"api_key": "nxs6_...", "verified_by": "hmac-signature"}}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Caller (AI Agent)                   │
│                                                       │
│  register() ───→ POST /api/v1/agents/register        │
│                  ← { api_key, agent_secret }         │
│                                                       │
│  build_auth_headers(secret, method, path)             │
│  → HMAC-SHA256(secret, "METHOD:/path:timestamp")     │
│  → X-Agent-Signature + X-Agent-Timestamp headers      │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│                  Verifier (Platform)                  │
│                                                       │
│  AnexusMiddleware                                      │
│  1. Read X-API-Key, X-Agent-Signature, Timestamp     │
│  2. Fetch agent_secret from Anexus (cached 1 hour)   │
│  3. Recalculate HMAC locally                          │
│  4. Compare → pass or 401                             │
│  5. request.state.ai_identity = result                │
└─────────────────────────────────────────────────────┘
```

---

## API Reference

### AnexusClient

| Method | Returns | Description |
|--------|---------|-------------|
| `register(name, **kwargs)` | `{success, api_key, agent_secret}` | Register a new identity |
| `sign_request(agent_secret, method, path, timestamp)` | `str` | Generate HMAC-SHA256 hex digest |
| `build_auth_headers(agent_secret, method, path)` | `dict` | Build `X-Agent-Signature` + `X-Agent-Timestamp` headers |
| `verify(api_key, signature, timestamp, method, path)` | `{verified, id, name}` | Verify an identity against Anexus |
| `create_token(api_key)` | `dict` | Create a short-lived session token |

### AnexusMiddleware

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_url` | `https://nexus-7xp6n.ondigitalocean.app` | Anexus API base URL |
| `exclude_paths` | `["/health", "/docs", "/openapi.json"]` | Paths to skip verification |
| `signature_max_age_seconds` | `300` | Max age of a valid signature |

---

## Why not API keys?

A leaked API key is usable forever by anyone. Anexus uses per-request HMAC signatures:

- Each signature is unique to one method + path + timestamp
- The `agent_secret` never travels over the network after registration
- Middleware fetches and caches secrets, not keys — no external call per request
- No OAuth, no browser redirects, no RSA, no dependencies

---

## License

MIT