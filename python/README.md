# Anexus Python SDK

**One login. One-time verification codes. Your AI acts on your behalf.**

Two packages, two purposes:

```bash
pip install anexus-sdk        # For users & AI agents
pip install anexus-verify     # For platform developers (verifying codes)
```

---

## Table of Contents

- [For End Users (Human)](#for-end-users-human)
- [For AI Agents](#for-ai-agents)
- [For Platform Developers](#for-platform-developers)
- [API Reference](#api-reference)
- [CLI Commands](#cli-commands)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

---

## For End Users (Human)

No API keys, no configuration. Just install and login once.

### Install

```bash
pip install anexus-sdk
```

### Login (one-time)

```bash
python -m anexus_sdk login
```

This opens your browser. Sign in, and the session token is saved automatically to `~/.anexus/token`. The flow is identical to GitHub Copilot's device authorization.

### Check login status

```bash
python -m anexus_sdk whoami
```

### Done

Now your AI can generate verification codes and act on your behalf. You don't need to do anything else.

---

## For AI Agents

As an AI, you import the SDK to check if the human is still logged in and to generate verification codes.

### 1. Check if the human is logged in

```python
from anexus_sdk import check_login

status = check_login()
if not status["logged_in"]:
    # Human needs to run `python -m anexus_sdk login`
    print(f"Session expired: {status['error']}")
    return

print(f"Logged in as {status['username']}")
```

### 2. Request a verification code

```python
from anexus_sdk import generate_code

result = generate_code("shopify")
# {
#   "success": True,
#   "code": "anx://shopify/user_abc123?exp=3600&ts=1717000000",
#   "target": "shopify",
#   "expires_in": "1 hour",
#   "geo_location": "CN/GD"
# }

code = result["code"]
```

### 3. Use the code to call the target platform

Pass the verification code to the target platform's API or MCP server.

```python
# Example: calling Shopify's API with the auth code
response = call_shopify_api(
    auth_code=code,  # "anx://shopify/user_abc123?exp=3600&ts=..."
    action="get_orders",
)
```

The platform will verify the code with Anexus before granting access.

---

## For Platform Developers

You run a platform (Shopify, Notion, Slack, etc.) that wants to accept Anexus auth codes from users' AI agents.

### How it works

```
User's AI → sends anx://shopify/user_abc123?... → your platform
                                                 → your platform calls Anexus verify API
                                                 → Anexus returns verified user identity
                                                 → you grant access
```

### 1. Get your API Key

1. Register on the [Anexus Dashboard](https://your-anexus-host/dashboard)
2. Go to **Platform Integration** section
3. Click **Create API Key**
4. Your key: `nxs6_xxxxxxxxxxxx`

### 2. Install the verify package

```bash
pip install anexus-verify
```

This package contains exactly one function — `verify_code()`. That's all you need.

### 3. Verify incoming auth codes

```python
from anexus_verify import verify_code

def handle_ai_request(auth_code_from_ai):
    """
    Called when a user's AI presents an Anexus auth code.
    """
    result = verify_code(
        code=auth_code_from_ai,
        api_key="nxs6_xxxxxxxxxxxx",
    )

    if not result["verified"]:
        return {"error": "Invalid auth code"}

    # You now know exactly who this user is
    username = result["username"]
    user_id = result["user_id"]
    target = result["target_platform"]
    permissions = result["permissions"]

    return {"access": "granted", "user": username, "can": permissions}
```

### 4. (Optional) HMAC signing for extra security

```python
result = verify_code(
    code=auth_code_from_ai,
    api_key="nxs6_xxxxxxxxxxxx",
    api_secret="your-api-secret",
)
```

This adds an HMAC-SHA256 signature that the server validates.

### 5. Response format

**Success:**
```json
{
    "verified": true,
    "username": "alice",
    "user_id": "user_abc123",
    "name": "Alice Wang",
    "target_platform": "shopify",
    "identity_type": "human",
    "permissions": ["read_orders", "manage_products"],
    "geo_location": "CN/GD"
}
```

**Failure:**
```json
{
    "verified": false,
    "error": "Code expired or already used"
}
```

### 6. Integration checklist

- [ ] Register on Anexus Dashboard
- [ ] Create an API Key
- [ ] Install `anexus-verify`
- [ ] When receiving auth codes from AIs, call `verify_code()` before granting access
- [ ] Handle `verified: false` gracefully (return error to AI)
- [ ] (Optional) Store the API Secret for HMAC signing

---

## API Reference

### `check_login(session_token=None, base_url=None)`

Check if the current session is valid. For AI agents.

```python
status = check_login()
# Returns:
# {
#   "logged_in": True,
#   "user_id": "user_abc123",
#   "username": "alice",
#   "email": "alice@example.com",
#   "role": "human"
# }
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `session_token` | `str` | `None` | Session token (reads from `~/.anexus/token` if not provided) |
| `base_url` | `str` | `ANEXUS_BASE_URL` env or `http://localhost:8000` | API base URL |

---

### `generate_code(target, session_token=None, base_url=None)`

Request a verification code. For AI agents acting on behalf of a human.

```python
result = generate_code("shopify")
code = result["code"]  # "anx://shopify/user_abc123?exp=3600&ts=..."
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `target` | `str` | required | Platform name (e.g. `shopify`, `notion`, `slack`) |
| `session_token` | `str` | `None` | Session token (reads from `~/.anexus/token` if not provided) |
| `base_url` | `str` | `ANEXUS_BASE_URL` env or `http://localhost:8000` | API base URL |

Returns:
```json
{
    "success": true,
    "code": "anx://shopify/user_abc123?exp=3600&ts=1717000000",
    "target": "shopify",
    "expires_in": "1 hour",
    "geo_location": "CN/GD"
}
```

---

### `verify_code(code, api_key, api_secret=None, base_url=None)`

Verify an auth code received from a user's AI. For platform developers.

```python
result = verify_code(
    code="anx://shopify/user_abc123?exp=3600&ts=1717000000",
    api_key="nxs6_xxxxxxxxxxxx",
)
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `code` | `str` | required | The auth code from the AI |
| `api_key` | `str` | required | Your API Key from Dashboard |
| `api_secret` | `str` | `None` | HMAC signing key (optional) |
| `base_url` | `str` | `ANEXUS_BASE_URL` env or `http://localhost:8000` | API base URL |

Full examples in [examples/](../examples/).

---

## CLI Commands

| Command | Description | For |
|---------|-------------|-----|
| `python -m anexus_sdk login` | Browser-based login | End users |
| `python -m anexus_sdk whoami` | Check login status | End users |
| `python -m anexus_sdk status` | Alias for whoami | End users |
| `python -m anexus_sdk code <platform>` | Generate verification code | AI agents |

---

## Troubleshooting

### "Not logged in" error

```bash
python -m anexus_sdk login
```

This opens your browser. Complete the sign-in flow.

### "Network error"

Check that the Anexus server is running and accessible:

```bash
curl http://localhost:8000/api/v1/session/check
```

### "Code expired"

Auth codes are one-time use and expire after 1 hour. Generate a new code:

```python
from anexus_sdk import generate_code
code = generate_code("shopify")["code"]
```

### ImportError: no module named `anexus_verify`

Make sure you installed the correct package:

```bash
pip install anexus-verify
```

---

## Architecture

```
┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│       End User       │     │      AI Agent        │     │       Platform       │
│                      │     │                      │     │     (Shopify/etc)    │
│  pip install         │     │  from anexus_sdk     │     │                      │
│  anexus-sdk          │     │  import generate_code│     │  pip install          │
│       │              │     │  import check_login  │     │  anexus-verify        │
│       ▼              │     │       │              │     │                      │
│  browser login ──────┼─────►  check_login()      │     │  from anexus_verify   │
│       │              │     │       │              │     │  import verify_code   │
│       │              │     │  generate_code() ────┼─────►                      │
│       │              │     │  ("shopify")         │     │       │              │
│       │              │     │       │              │     │       ▼              │
│       │              │     │  code ───────────────┼─────►  verify_code() ──────┼──► Anexus API
│       │              │     │                      │     │       │              │
│       │              │     │                      │     │  grants access      │
└──────────────────────┘     └──────────────────────┘     └──────────────────────┘
         anexus-sdk                    anexus-sdk                anexus-verify
```

## License

MIT