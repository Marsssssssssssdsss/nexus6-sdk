# Anexus SDK — Auth Codes for AI Agents

Let your AI act on your behalf. One login, one-time verification codes for any platform.

```
pip install git+https://github.com/Marsssssssssssdsss/nexus6-sdk.git#subdirectory=python
```

## Quick Start

### 1. Login (human, one-time)

```bash
python -m anexus_sdk login
```

Opens your browser → you sign in → session token saved automatically.  
Just like GitHub Copilot's device flow.

### 2. Generate a verification code (AI does this)

```python
from anexus_sdk import generate_code

result = generate_code("shopify")
code = result["code"]  # anx://shopify/user_xxx?exp=3600&ts=...
```

Or via CLI:

```bash
python -m anexus_sdk code shopify
```

### 3. Use the code to call the target platform

Your AI passes the code (e.g., `anx://shopify/user_xxx?exp=3600&ts=...`) to the target platform's API or MCP server. The platform verifies it by calling our API.

## For Platform Developers

Verify incoming auth codes with your API Key:

```bash
curl -X POST https://your-anexus-host/api/v1/codes/verify \
  -H "x-api-key: nxs6_xxx" \
  -d '{"code": "anx://shopify/user_xxx?exp=3600&ts=..."}'
```

Get your API Key from the [Dashboard](https://your-anexus-host/dashboard).

## SDK Reference

### `generate_code(target, session_token=None, base_url=None)`

Request a one-time verification code for a target platform.

| Param | Type | Description |
|-------|------|-------------|
| `target` | `str` | Platform name (e.g., `shopify`, `notion`, `slack`) |
| `session_token` | `str` | Optional. Reads from `~/.anexus/token` if not provided |
| `base_url` | `str` | Optional. API base URL |

Returns:

```json
{
  "success": true,
  "code": "anx://shopify/user_xxx?exp=3600&ts=...",
  "target": "shopify",
  "expires_in": "1 hour",
  "geo_location": ""
}
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `python -m anexus_sdk login` | Browser-based login (GitHub Copilot style) |
| `python -m anexus_sdk code <platform>` | Generate verification code |

## Architecture

```
Human                     AI Agent                    Target Platform
  │                          │                              │
  │── login (browser) ──────►                              │
  │                          │                              │
  │                    generate_code("shopify")             │
  │                          │                              │
  │                          │── anx://shopify/... ────────►│
  │                          │                              ├── POST /codes/verify
  │                          │                              │── verified → allow
  │                          │◄──── response ──────────────│
```

## License

MIT