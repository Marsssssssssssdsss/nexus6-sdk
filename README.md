# Anexus — Auth Codes for AI Agents

One login. Your AI gets one-time verification codes to act on your behalf.

```
pip install git+https://github.com/Marsssssssssssdsss/nexus6-sdk.git#subdirectory=python
```

## Quick Start

```bash
python -m anexus_sdk login     # Browser login (GitHub Copilot style)
python -m anexus_sdk code shopify  # Generate verification code
```

```python
from anexus_sdk import generate_code
code = generate_code("shopify")["code"]
# anx://shopify/user_xxx?exp=3600&ts=...
```

## SDKs

- [Python SDK](python/) — `login`, `generate_code`, CLI
- [JavaScript SDK](javascript/) — coming soon

## How it works

1. **Human logs in** — one-time browser login, token saved automatically
2. **AI gets a code** — calls `generate_code("shopify")` from the SDK
3. **AI calls platform** — passes the code, platform verifies via our API

## License

MIT