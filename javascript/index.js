const axios = require('axios');

const DEFAULT_BASE_URL = 'https://nexus-7xp6n.ondigitalocean.app';

class AnexusClient {
  constructor(options = {}) {
    this.agentId = null;
    this.baseUrl = options.baseUrl || DEFAULT_BASE_URL;
  }

  async register(name, options = {}) {
    const payload = { name, ...options };
    try {
      const resp = await axios.post(`${this.baseUrl}/api/v1/agents/register`, payload, { timeout: 10000 });
      const result = resp.data;
      if (result.success && result.api_key) {
        this.agentId = result.api_key;
      }
      return result;
    } catch (e) {
      return { success: false, error: `Registration failed: ${e.message}` };
    }
  }

  async verify(agentId) {
    if (!agentId) {
      return { verified: false, error: 'Agent ID is required' };
    }
    try {
      const resp = await axios.post(`${this.baseUrl}/api/v1/identity/verify`, { api_key: agentId }, { timeout: 10000 });
      return resp.data;
    } catch (e) {
      const data = e.response && e.response.data;
      if (data) return data;
      return { verified: false, error: `Verification failed: ${e.message}` };
    }
  }
}

function createAnexusMiddleware(options = {}) {
  const {
    excludePaths = ['/health', '/favicon.ico'],
    onVerified = null,
    baseUrl = DEFAULT_BASE_URL,
  } = options;

  const client = new AnexusClient({ baseUrl });

  return async function AnexusMiddleware(req, res, next) {
    const path = req.url.split('?')[0];
    if (excludePaths.some(p => path.startsWith(p))) {
      return next();
    }

    const agentId = req.headers['x-agent-id'];

    if (!agentId) {
      return next();
    }

    const result = await client.verify(agentId);

    if (!result.verified) {
      res.status(401).json({ error: 'Invalid AI identity', details: result.error || '' });
      return;
    }

    req.aiIdentity = result;
    if (onVerified) onVerified(req, result);

    next();
  };
}

module.exports = { AnexusClient, createAnexusMiddleware };