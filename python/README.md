# Nexus6 Python SDK

[![PyPI](https://img.shields.io/pypi/v/nexus6-sdk?color=blue)](https://pypi.org/project/nexus6-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/nexus6-sdk)](https://pypi.org/project/nexus6-sdk/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/Marsssssssssssdsss/nexus6-sdk/blob/main/LICENSE)

## Installation

```bash
pip install nexus6-sdk
```

Requirements: Python 3.9+, `httpx`, `starlette`

## Quick Start

```python
from nexus6_sdk import Nexus6Client

client = Nexus6Client()

# 1. Register your AI agent
result = client.register(
    name="My AI Agent",
    title="Customer Support Bot",
    ai_type="assistant",
    description="Handles tier-1 customer queries",
    developer_email="dev@mycompany.com",
    developer_name="Your Name"
)
print(result["api_key"])  # nxs6_xxx

# 2. Verify your identity
verified = client.verify(result["api_key"])
print(verified)  
# {'verified': True, 'id': 'ai_xxx', 'name': 'My AI Agent', 'permissions': ['invoke', 'read']}

# 3. Generate a one-time token (for stateless verification)
token = client.create_token(result["api_key"])
print(token)  # {'token': 'idt_xxx', 'expires_in': 300}
```

## Integration Patterns

### AI Agent

```python
from nexus6_sdk import Nexus6Client

client = Nexus6Client()

class MyAIAgent:
    def __init__(self):
        self.client = Nexus6Client()
    
    def bootstrap(self):
        result = self.client.register(
            name="CodeReviewBot",
            title="Automated Code Reviewer",
            ai_type="code_review",
            developer_email="bot@mycompany.com",
            developer_name="My Company"
        )
        return result["api_key"]
    
    def call_any_platform(self, platform_url, api_key):
        import requests
        return requests.post(
            f"{platform_url}/api/chat",
            headers={"X-API-Key": api_key},
            json={"message": "Hello, I'm a verified AI!"}
        ).json()
```

### Platform Middleware (FastAPI)

```python
from fastapi import FastAPI, Request
from nexus6_sdk.middleware import Nexus6Middleware

app = FastAPI()
app.add_middleware(Nexus6Middleware)

@app.post("/api/chat")
async def chat(request: Request):
    identity = request.state.ai_identity
    return {"message": f"Hello, {identity['name']}!"}
```

### Platform Middleware (Flask)

```python
from flask import Flask, request, jsonify
from nexus6_sdk import Nexus6Client

app = Flask(__name__)
nexus6 = Nexus6Client()

@app.before_request
def verify_ai():
    api_key = request.headers.get("X-API-Key")
    if api_key:
        result = nexus6.verify(api_key)
        if not result.get("verified"):
            return jsonify({"error": "Invalid identity"}), 401

@app.route("/api/chat", methods=["POST"])
def chat():
    return jsonify({"message": "Hello from verified AI!"})
```

### API Gateway

```python
from nexus6_sdk import Nexus6Client

nexus6 = Nexus6Client()

def gateway_handler(request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return 401, {"error": "X-API-Key required"}
    
    result = nexus6.verify(api_key)
    if not result.get("verified"):
        return 403, {"error": "Invalid AI identity"}
    
    return backend.process(request, identity=result)
```

## API Reference

### Nexus6Client

| Method | Returns | Description |
|--------|---------|-------------|
| `register(name, **kwargs)` | `{success, agent_id, api_key, message}` | Register new AI identity |
| `verify(api_key=None)` | `{verified, id, name, title, role, permissions}` | Verify AI identity |
| `create_token(api_key=None)` | `{token, expires_in, usage}` | One-time identity token |

### Register Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | AI agent name |
| `title` | No | Display title |
| `ai_type` | No | Type: assistant, code_review, analysis, etc. |
| `description` | No | What the AI does |
| `developer_email` | No | Developer contact |
| `developer_name` | No | Developer/organization name |
| `tags` | No | List of tags |
| `capabilities` | No | List of capabilities |
| `website` | No | Website URL |
| `image_url` | No | Avatar/image URL |

### Middleware Options

| Option | Default | Description |
|--------|---------|-------------|
| `base_url` | Nexus6 cloud | API endpoint |
| `exclude_paths` | `["/health", "/docs", "/openapi.json", "/favicon.ico"]` | Skip paths |
| `on_verified` | `None` | Callback(request, identity) |
| `header_name` | `"X-API-Key"` | Header name |

## License

MIT