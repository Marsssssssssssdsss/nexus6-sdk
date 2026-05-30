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

### 2. Check login status

```bash
python -m anexus_sdk whoami
```

Or from Python:

```python
from anexus_sdk import check_login
status = check_login()
if status["logged_in"]:
    print(f"Logged in as {status['username']}")
```

### 3. Generate a verification code (AI does this)

```python
from anexus_sdk import generate_code

result = generate_code("shopify")
code = result["code"]  # anx://shopify/user_xxx?exp=3600&ts=...
```

Or via CLI:

```bash
python -m anexus_sdk code shopify
```

### 4. Use the code to call the target platform

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

### `check_login(session_token=None, base_url=None)`

Check if the current session is still valid. AI agents should call this before `generate_code()`.

```python
status = check_login()
if status["logged_in"]:
    print(status["username"])  # e.g. "alice"
else:
    print(status["error"])     # e.g. "Session expired"
```

Returns:

| Key | Type | Description |
|-----|------|-------------|
| `logged_in` | `bool` | Whether the session is active |
| `user_id` | `str` | (if logged in) User ID |
| `username` | `str` | (if logged in) Username |
| `email` | `str` | (if logged in) Email |
| `role` | `str` | (if logged in) User role |
| `error` | `str` | (if not logged in) Error message |

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
| `python -m anexus_sdk whoami` | Check login status |
| `python -m anexus_sdk code <platform>` | Generate verification code |
| `python -m anexus_sdk status` | Alias for `whoami` |

## Architecture

```
Human                     AI Agent                    Target Platform
  │                          │                              │
  │── login (browser) ──────►                              │
  │                          │                              │
  │                    check_login()                        │
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