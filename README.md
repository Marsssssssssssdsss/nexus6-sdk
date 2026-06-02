<div align="center">

# AI Agent Identity — verify which agent is calling your API

When an AI agent shows up at your API endpoint, how do you know it's really who it claims to be?

<p align="center">
  <a href="https://pypi.org/project/anexus-sdk/"><img src="https://img.shields.io/pypi/v/anexus-sdk?label=anexus-sdk&color=3b82f6" /></a>
  <a href="https://pypi.org/project/anexus-verify/"><img src="https://img.shields.io/pypi/v/anexus-verify?label=anexus-verify&color=a855f7" /></a>
  <a href="python/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" /></a>
</p>

<p align="center">
  <a href="#the-problem">The Problem</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="python/">Docs</a> •
  <a href="examples/">Examples</a>
</p>

</div>

---

## The Problem

Three things are true right now:

1. AI agents are calling more and more APIs — your users' agents want to query their Shopify, read their Notion, send emails on their behalf
2. The only way to give an agent access today is to share a permanent API key or a session cookie — which means the agent has indefinite access, and if that key leaks, so does everything it protects
3. When an agent calls your API, you have no way to verify: is this a real agent acting on behalf of a real user, or someone impersonating one?

This repo is a working implementation that solves all three.

## How It Works

Instead of sharing permanent secrets, the user authenticates once (standard OAuth), and the agent generates short-lived, scoped verification codes on demand.

```
End User              AI Agent              Platform API
  │                      │                      │
  │── login once ───────►│                      │
  │                      │── generate_code() ──►│
  │                      │   (scoped, 1hr TTL)  │
  │                      │                      │── verify_code()
  │                      │                      │   → returns user identity
  │                      │◄── access granted ───│
```

**What each side does:**

| Side | What they get | What it solves |
|------|--------------|----------------|
| **End user** | Log in once, their AI acts for them without sharing permanent keys | No more "here's my API key, don't lose it" |
| **AI agent** | Generates a verification code per-platform, per-session | Agent has exactly the access it needs, for exactly as long as it needs |
| **Platform API** | Receives a code, calls `verify_code()`, gets back who the user is | Never needs to store agent credentials, just verifies on the fly |

## Quick Start

### For an end user

```bash
pip install anexus-sdk
python -m anexus_sdk login    # Opens browser → sign in → token saved locally
```

### For an AI agent

```python
from anexus_sdk import generate_code

code = generate_code("shopify")["code"]
# → returns a one-time verification code, valid for 1 hour
# Pass this code instead of an API key
```

### For a platform that accepts AI agent calls

```bash
pip install anexus-verify
```

```python
from anexus_verify import verify_code

# In your endpoint:
result = verify_code(
    code="anx://shopify/user_abc123?exp=3600&ts=1717000000",
    api_key="nxs6_xxxxxxxxxxxx",
)

if result["verified"]:
    grant_access(result["username"], result["permissions"])
```

## The Difference This Makes

**Without this approach:**
- API keys live in `.env` files that agents can read and exfiltrate
- A leaked key means permanent access until manually revoked
- No audit trail for which agent did what

**With this approach:**
- No permanent secrets stored where the agent can read them
- Every access is scoped to a specific platform and expires automatically
- The platform sees exactly which user authorized the call

## Examples

- [Flask integration](examples/python/flask_platform.py) — verify agent identity in a Flask app
- [FastAPI integration](examples/python/fastapi_platform.py) — verify in a FastAPI app
- [AI Agent workflow](examples/python/ai_agent.py) — generate codes as an AI agent
- [Express.js middleware](examples/javascript/express_middleware.js) — verify in Node.js

## License

MIT