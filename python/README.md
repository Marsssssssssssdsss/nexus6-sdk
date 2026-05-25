# Anexus Python SDK

[![PyPI](https://img.shields.io/pypi/v/Anexus-sdk?color=blue)](https://pypi.org/project/Anexus-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/Anexus-sdk)](https://pypi.org/project/Anexus-sdk/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/Marsssssssssssdsss/Anexus-sdk/blob/main/LICENSE)

## Installation

```bash
pip install Anexus-sdk
```

## Quick Start — Register a new AI agent

```python
from Anexus_sdk import AnexusClient

client = AnexusClient()

# Register — you get an identity + RSA key pair
result = client.register(name="My AI Agent")
print(result["api_key"])      # nxs6_xxx — your identifier
print(result["public_key"])   # RSA public key (stored on Anexus)
print(result["private_key"])  # RSA private key — save securely!
```

## Quick Start — Sign and verify (5 lines)

```python
import time
from Anexus_sdk import AnexusClient

client = AnexusClient()

# 1. Sign a request with your private key
message = f"POST:/api/v1/tools:{int(time.time())}"
signature = client.sign_request(private_key_pem, message)

# 2. Verify on the other side
result = client.verify(
    api_key="nxs6_xxx",
    signature=signature,
    timestamp=str(int(time.time())),
    method="POST",
    path="/api/v1/tools"
)
print(result["verified"])  # True
```

## How It Works

```
AI Agent                          Platform
    │                                 │
    ├─ Register → get RSA keys        │
    │                                 │
    ├─ sign_request(private_key,      │
    │   "GET:/api/data:ts")           │
    │                                 │
    ├─ Send headers:                  │
    │   X-API-Key: nxs6_xxx           │
    │   X-Agent-Signature: <base64>   │
    │   X-Agent-Timestamp: <ts>       │
    │                       ─────►    │
    │                                 ├─ Lookup public key by api_key
    │                                 ├─ Verify RSA signature locally
    │                                 ├─ ✅ Identity verified (under 100ms)
    │                                 └─ Process request
```

## Platform Integration (FastAPI)

One line of middleware. Every incoming request is verified automatically.

```python
from fastapi import FastAPI, Request
from Anexus_sdk.middleware import AnexusMiddleware

app = FastAPI()
app.add_middleware(AnexusMiddleware)

@app.post("/api/chat")
async def chat(request: Request):
    identity = request.state.ai_identity
    return {"message": f"Verified AI: {identity['identity']['api_key']}"}
```

### Expected Headers

| Header | Value | Required |
|--------|-------|----------|
| `X-API-Key` | `nxs6_xxx` | Yes |
| `X-Agent-Signature` | base64(RSA-SHA256) | Yes |
| `X-Agent-Timestamp` | Unix timestamp | Yes |

### Custom Configuration

```python
app.add_middleware(
    AnexusMiddleware,
    base_url="https://your-Anexus-instance.com",
    exclude_paths=["/health", "/docs"],
    signature_max_age_seconds=60,  # default: 300
)
```

## API Reference

### AnexusClient

| Method | Returns | Description |
|--------|---------|-------------|
| `register(name, **kwargs)` | `{success, agent_id, api_key, private_key, public_key}` | Register new AI agent with RSA keys |
| `verify(api_key, signature, timestamp, method, path)` | `{verified, id, name, ...}` | Verify RSA signature against Anexus |
| `sign_request(private_key_pem, message)` | `str` | Sign a message with RSA private key |
| `build_auth_headers(private_key_pem, method, path)` | `{X-Agent-Signature, X-Agent-Timestamp}` | Build signature headers |
| `generate_keys(ai_id, x_api_key)` | `{success, public_key, private_key}` | Generate RSA key pair and upload public key |
| `fetch_public_key(ai_id)` | `str or None` | Fetch public key by agent ID |
| `fetch_public_key_by_api_key(api_key)` | `str or None` | Fetch public key by API key |
| `verify_signature_offline(public_key_pem, message, signature)` | `bool` | Verify RSA signature locally |

### Register Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | AI agent name |
| `title` | No | Display title |
| `ai_type` | No | Type: assistant, coding, customer_service, etc. |
| `description` | No | What the AI does |
| `developer_email` | No | Developer contact |

### Middleware Options

| Option | Default | Description |
|--------|---------|-------------|
| `base_url` | `https://nexus-7xp6n.ondigitalocean.app` | Anexus API endpoint |
| `mode` | `"signature"` | Verification mode (signature or legacy) |
| `exclude_paths` | `["/health", "/docs", ...]` | Paths to skip |
| `signature_max_age_seconds` | `300` | Max signature age (5 min) |
| `on_verified` | `None` | Callback(request, identity) |

## Requirements

- Python 3.9+
- `httpx`
- `starlette` (for middleware)
- `cryptography` (for RSA signing/verification)

## License

MIT