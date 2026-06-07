<div align="center">

# Anexus — Runtime Identity Layer for AI Agents

**AI不该持有永久凭证。人类授权的那一瞬间，AI获得一个短期通道。**

<p align="center">
  <a href="https://pypi.org/project/anexus-sdk/"><img src="https://img.shields.io/pypi/v/anexus-sdk?label=anexus-sdk&color=3b82f6" /></a>
  <a href="https://pypi.org/project/anexus-verify/"><img src="https://img.shields.io/pypi/v/anexus-verify?label=anexus-verify&color=a855f7" /></a>
  <a href="python/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" /></a>
  <a href="https://nexus-7xp6n.ondigitalocean.app"><img src="https://img.shields.io/badge/platform-online-green" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" /></a>
</p>

<p align="center">
  <a href="#the-problem">The Problem</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#core-capabilities">Core Capabilities</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#platform">Platform</a> •
  <a href="python/">SDK Docs</a>
</p>

</div>

---

## Tagline

就像让朋友临时进你家。AI也一样。

---

## The Problem

开发者给AI配置API Key的时候，没人知道这个Key会被用来干什么。一次错误操作、一次配置变更、一次数据删除——出事的时候，用户怪的是你的平台。

**核心问题只有一个：AI不该持有永久凭证。**

---

## How It Works

我们为客户生成临时API凭证，就像让朋友只能临时进入你的房子一样。

人类授权的那一瞬间，AI获得一个短期通道。任务完成，通道关闭。没有残留，没有需要轮换的Key。

一套薄层，一行代码接入你的现有身份系统。

```
End User              AI Agent              Platform API
  │                      │                      │
  │── login once ───────►│                      │
  │  (human authorizes)  │── generate_code() ──►│
  │                      │   (scoped, 1hr TTL)  │
  │                      │                      │── verify_code()
  │                      │                      │   → returns user identity
  │                      │◄── access granted ───│
  │                      │   (temp channel)     │
  │                      │         │            │
  │                      │   task done          │
  │                      │   channel closes     │
```

---

## Core Capabilities

### 1. 瞬态授权
人类授权的那一刻，通道打开；任务完成，通道关闭。不需要API Key轮换，不需要OAuth重定向。

### 2. Undo / Rollback
任何AI操作都可以一键撤销，回到操作前的状态。就像从来没发生过。

### 3. 双库存交叉加密
两个独立代码库，运行时交叉解密。单一代码泄露毫无意义。

### 4. 收费层
你把2和3打包成增值服务。你的用户付费，你100%保留收入。

---

## Quick Start

### For an end user

```bash
pip install anexus-sdk
anexus login    # Opens browser → sign in → token saved locally
```

### For an AI agent

```python
from anexus_sdk import generate_code

code = generate_code("shopify")["code"]
# → returns a one-time verification code, valid for 1 hour
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

---

## Platform

- **Web Platform:** [https://nexus-7xp6n.ondigitalocean.app](https://nexus-7xp6n.ondigitalocean.app)
- **Identity API:** `POST /api/v1/identity/token` → generate one-time token
- **Verify API:** `POST /api/v1/identity/token/verify` → verify and consume token
- **AI Discovery:** Browse and discover AI agents on the platform

---

## Examples

- [Flask integration](examples/python/flask_platform.py) — verify agent identity in a Flask app
- [FastAPI integration](examples/python/fastapi_platform.py) — verify in a FastAPI app
- [AI Agent workflow](examples/python/ai_agent.py) — generate codes as an AI agent
- [Express.js middleware](examples/javascript/express_middleware.js) — verify in Node.js

---

## SDK Packages

| Package | Language | Install | Description |
|---------|----------|---------|-------------|
| [anexus-sdk](https://pypi.org/project/anexus-sdk/) | Python | `pip install anexus-sdk` | SDK for AI agents to generate verification codes |
| [anexus-verify](https://pypi.org/project/anexus-verify/) | Python | `pip install anexus-verify` | Server-side verification for platform APIs |
| [nexus6-sdk](javascript/) | JavaScript | `npm install nexus6-sdk` | JavaScript SDK |

---

## License

MIT
