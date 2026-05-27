# Anexus JavaScript SDK

## Server side (Express middleware)

```bash
npm install github:Marsssssssssssdsss/nexus6-sdk
```

```javascript
const { createAnexusMiddleware } = require('anexus-sdk/javascript');
app.use(createAnexusMiddleware());
```

Requests with `X-API-Key` header are verified. Requests without it pass through.

```javascript
app.get('/api/v1/tools', (req, res) => {
  const identity = req.aiIdentity;
  // { verified: true, identity: { api_key: '...', verified_by: 'hmac-signature' } }
});
```

## Agent side (signing requests)

```javascript
const { signRequest } = require('anexus-sdk/javascript');
const headers = signRequest('GET', '/api/v1/tools', agentSecret, apiKey);
```

## Configuration

```javascript
createAnexusMiddleware({
  baseUrl: 'https://nexus-7xp6n.ondigitalocean.app',
  excludePaths: ['/health', '/docs'],
  signatureMaxAgeSeconds: 300,
});
```

## License

MIT