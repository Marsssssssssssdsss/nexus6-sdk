# Anexus SDK

AI identity for your MCP server. One header, one line.

## Python (FastAPI)

```bash
pip install git+https://github.com/Marsssssssssssdsss/nexus6-sdk.git#subdirectory=python
```

```python
from anexus_sdk.middleware import AnexusMiddleware
app.add_middleware(AnexusMiddleware)
```

Done. Every request with `X-Agent-ID` header is verified automatically.

## JavaScript (Express)

```bash
npm install github:Marsssssssssssdsss/nexus6-sdk
```

```javascript
const { createAnexusMiddleware } = require('anexus-sdk/javascript');
app.use(createAnexusMiddleware());
```

## How it works

An agent registers once and gets a permanent identity:

```python
from anexus_sdk import AnexusClient

client = AnexusClient()
result = client.register("my-agent")
# → stores this agent_id forever:
agent_id = result["api_key"]  # nxs6_xxxxxxxxx
```

Every request just sends the agent_id in a header:

```
X-Agent-ID: nxs6_xxxxxxxxx
```

The middleware checks it against our service and caches the result for 1 hour. That's it. No signing, no tokens, no expiry.

## Docs

- Python SDK: [python/README.md](python/README.md)
- JavaScript SDK: [javascript/README.md](javascript/README.md)

## License

MIT