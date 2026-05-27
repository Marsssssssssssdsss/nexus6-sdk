# Anexus SDK

Verify AI Agent identity on your MCP Server with 1 line of middleware.

## Python (FastAPI)

```bash
pip install git+https://github.com/Marsssssssssssdsss/nexus6-sdk.git#subdirectory=python
```

```python
from anexus_sdk.middleware import AnexusMiddleware
app.add_middleware(AnexusMiddleware)
```

That's it. Every request with `X-API-Key` + `X-Agent-Signature` headers is verified automatically.

## JavaScript (Express)

```bash
npm install github:Marsssssssssssdsss/nexus6-sdk
```

```javascript
const { createAnexusMiddleware } = require('anexus-sdk/javascript');
app.use(createAnexusMiddleware());
```

## Docs

- Python SDK: [python/README.md](python/README.md)
- JavaScript SDK: [javascript/README.md](javascript/README.md)
- Live API: https://nexus-7xp6n.ondigitalocean.app

## License

MIT