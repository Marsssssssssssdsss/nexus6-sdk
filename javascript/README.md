# Nexus6 JavaScript SDK

[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/Marsssssssssssdsss/nexus6-sdk/blob/main/LICENSE)
[![npm install](https://img.shields.io/badge/npm-install-blue)](https://github.com/Marsssssssssssdsss/nexus6-sdk)

## Installation

```bash
npm install github:Marsssssssssssdsss/nexus6-sdk
```

Requirements: Node.js 16+, `axios`

## Quick Start

```javascript
const { Nexus6Client } = require('nexus6-sdk/javascript');

const client = new Nexus6Client();

// 1. Register your AI agent
const result = await client.register('My AI Agent', {
  title: 'Customer Support Bot',
  ai_type: 'assistant',
  description: 'Handles tier-1 customer queries',
  developer_email: 'dev@mycompany.com',
  developer_name: 'Your Name'
});
console.log(result.api_key);  // nxs6_xxx

// 2. Verify your identity
const verified = await client.verify(result.api_key);
console.log(verified);
// { verified: true, id: 'ai_xxx', name: 'My AI Agent', permissions: ['invoke', 'read'] }

// 3. Generate a one-time token
const token = await client.createToken(result.api_key);
console.log(token);  // { token: 'idt_xxx', expires_in: 300 }
```

## Integration Patterns

### AI Agent

```javascript
const { Nexus6Client } = require('nexus6-sdk/javascript');

class MyAIAgent {
  constructor() {
    this.client = new Nexus6Client();
  }

  async bootstrap() {
    const result = await this.client.register('CodeReviewBot', {
      title: 'Automated Code Reviewer',
      ai_type: 'code_review',
      developer_email: 'bot@mycompany.com',
      developer_name: 'My Company'
    });
    return result.api_key;
  }

  async callPlatform(platformUrl, apiKey) {
    const axios = require('axios');
    const response = await axios.post(
      `${platformUrl}/api/chat`,
      { message: "Hello, I'm a verified AI!" },
      { headers: { 'X-API-Key': apiKey } }
    );
    return response.data;
  }
}
```

### Platform Middleware (Express.js)

```javascript
const express = require('express');
const { createNexus6Middleware } = require('nexus6-sdk/javascript');

const app = express();
app.use(createNexus6Middleware());

app.post('/api/chat', (req, res) => {
  // req.aiIdentity is auto-populated
  res.json({ message: `Hello, ${req.aiIdentity.name}!` });
});

app.get('/api/whoami', (req, res) => {
  res.json({
    id: req.aiIdentity.id,
    name: req.aiIdentity.name,
    verified: req.aiIdentity.verified
  });
});

app.listen(3000);
```

### Standalone Verification

```javascript
const { Nexus6Client } = require('nexus6-sdk/javascript');

async function verifyRequest(req) {
  const client = new Nexus6Client();
  const apiKey = req.headers['x-api-key'];
  
  if (!apiKey) {
    throw new Error('X-API-Key required');
  }
  
  const result = await client.verify(apiKey);
  if (!result.verified) {
    throw new Error('Invalid AI identity');
  }
  
  return result;
}

// Usage in any HTTP framework
app.post('/api/secure', async (req, res) => {
  try {
    const identity = await verifyRequest(req);
    res.json({ message: `Welcome, ${identity.name}!` });
  } catch (e) {
    res.status(403).json({ error: e.message });
  }
});
```

## API Reference

### Nexus6Client

| Method | Returns | Description |
|--------|---------|-------------|
| `register(name, options)` | `{success, agent_id, api_key, message}` | Register new AI identity |
| `verify(apiKey)` | `{verified, id, name, title, role, permissions}` | Verify AI identity |
| `createToken(apiKey)` | `{token, expires_in, usage}` | One-time identity token |

### Register Options

| Option | Required | Description |
|--------|----------|-------------|
| `title` | No | Display title |
| `ai_type` | No | Type: assistant, code_review, analysis, etc. |
| `description` | No | What the AI does |
| `developer_email` | No | Developer contact |
| `developer_name` | No | Developer/organization name |
| `tags` | No | Array of tags |
| `capabilities` | No | Array of capabilities |
| `website` | No | Website URL |
| `image_url` | No | Avatar/image URL |

### Middleware Options

| Option | Default | Description |
|--------|---------|-------------|
| `headerName` | `"X-API-Key"` | Header name |
| `excludePaths` | `["/health", "/favicon.ico"]` | Skip paths |
| `onVerified` | `null` | Callback(req, identity) |
| `baseUrl` | Nexus6 cloud | Verification endpoint |

## License

MIT