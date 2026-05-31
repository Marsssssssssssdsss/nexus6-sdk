<div align="center">

# Anexus

**Auth codes for AI agents. One login, your AI acts on your behalf.**

<p align="center">
  <a href="https://pypi.org/project/anexus-sdk/"><img src="https://img.shields.io/pypi/v/anexus-sdk?label=anexus-sdk&color=3b82f6" /></a>
  <a href="https://pypi.org/project/anexus-verify/"><img src="https://img.shields.io/pypi/v/anexus-verify?label=anexus-verify&color=a855f7" /></a>
  <a href="python/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" /></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#use-cases">Use Cases</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="python/">Documentation</a> •
  <a href="examples/">Examples</a>
</p>

</div>

---

## Quick Start

### For end users

```bash
pip install anexus-sdk
python -m anexus_sdk login    # Opens browser → sign in → token saved
```

### For AI agents

```python
from anexus_sdk import generate_code

code = generate_code("shopify")["code"]
# → "anx://shopify/user_abc123?exp=3600&ts=1717000000"
# Pass this code to the target platform
```

### For platform developers

```bash
pip install anexus-verify
```

```python
from anexus_verify import verify_code

result = verify_code(
    code="anx://shopify/user_abc123?exp=3600&ts=1717000000",
    api_key="nxs6_xxxxxxxxxxxx",
)

if result["verified"]:
    grant_access(result["username"], result["permissions"])
```

---

## Use Cases

| Scenario | Without Anexus | With Anexus |
|----------|---------------|-------------|
| AI needs to query your Shopify orders | Share a permanent API token (risky) | Generate a one-time code, valid for 1 hour |
| AI needs to read your Notion docs | Paste your session cookie (insecure) | Generate a scoped code, expires automatically |
| Platform accepts AI agent calls | Build your own OAuth + identity system | Use `verify_code()` — 5 lines of code |
| User wants AI to act on their behalf | Manual delegation, no standard | Login once, AI generates codes automatically |

---

## How It Works

```
         ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
         │   End User   │         │   AI Agent   │         │   Platform   │
         │              │         │              │         │  (Shopify)   │
         │ login once ──┼────────►│ check_login()│         │              │
         │              │         │      │       │         │              │
         │              │         │ generate_    │         │              │
         │              │         │ code("shop"  │         │              │
         │              │         │      │       │         │              │
         │              │         │  code ───────┼────────►│ verify_code()│
         │              │         │              │         │      │       │
         │              │         │              │         │ grant access │
         └──────────────┘         └──────────────┘         └──────────────┘
           anexus-sdk                anexus-sdk              anexus-verify
```

1. **User logs in once** — browser-based OAuth, token saved locally
2. **AI checks login** — `check_login()` ensures session is valid
3. **AI requests a code** — `generate_code("shopify")` returns a one-time verification code
4. **AI sends code to platform** — the code is passed to the target platform's API
5. **Platform verifies** — `verify_code(code, api_key)` returns the user's identity
6. **Access granted** — platform knows exactly who this user is and what they can do

---

## Packages

| Package | Install | For | Contains |
|---------|---------|-----|----------|
| `anexus-sdk` | `pip install anexus-sdk` | End users & AI agents | `login`, `check_login()`, `generate_code()` |
| `anexus-verify` | `pip install anexus-verify` | Platform developers | `verify_code()` |

---

## Why Auth Codes?

**Before — sharing secrets is dangerous:**
```
User shares API key with AI → AI has permanent access → key can be leaked
```

**With Anexus — codes are scoped and temporary:**
```
User logs in once → AI generates anx://shopify/user_xxx?exp=3600&ts=...
                      ↑ exp=3600 → expires in 1 hour
                      ↑ ts=... → timestamped, prevents replay
                      ↑ user=xxx → identifies the user
                      ↑ one-time use → cannot be reused
```

---

## Examples

See the [examples/](examples/) directory for complete integrations:

- [Flask platform integration](examples/python/flask_platform.py) — Verify codes in a Flask app
- [FastAPI platform integration](examples/python/fastapi_platform.py) — Verify codes in a FastAPI app
- [AI Agent workflow](examples/python/ai_agent.py) — Generate codes as an AI agent
- [Express.js middleware](examples/javascript/express_middleware.js) — Verify codes in Node.js

---

## Documentation

Full documentation is in the [Python SDK directory](python/).

---

## License

MIT