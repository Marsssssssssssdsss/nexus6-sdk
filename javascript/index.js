const axios = require('axios');
const crypto = require('crypto');

const DEFAULT_BASE_URL = 'https://nexus-7xp6n.ondigitalocean.app';

class Nexus6Client {
  constructor(options = {}) {
    this.apiKey = options.apiKey || null;
    this.baseUrl = options.baseUrl || DEFAULT_BASE_URL;
  }

  async verify(apiKey, { signature, timestamp, method, path } = {}) {
    const key = apiKey || this.apiKey;
    if (!key) {
      return { verified: false, error: 'No API key provided. Pass apiKey or set it in client.' };
    }
    try {
      const body = { api_key: key };
      if (signature && timestamp) {
        body.signature = signature;
        body.timestamp = timestamp;
        body.method = method || 'POST';
        body.path = path || '/api/v1/identity/verify';
      }
      const resp = await axios.post(`${this.baseUrl}/api/v1/identity/verify`, body, { timeout: 10000 });
      return resp.data;
    } catch (e) {
      const data = e.response && e.response.data;
      if (data) return data;
      return { verified: false, error: `Verification failed: ${e.message}` };
    }
  }

  async register(name, options = {}) {
    const payload = { name, ...options };
    try {
      const resp = await axios.post(`${this.baseUrl}/api/ai/register`, payload, { timeout: 10000 });
      const result = resp.data;
      if (result.success && result.api_key) {
        this.apiKey = result.api_key;
      }
      return result;
    } catch (e) {
      return { success: false, error: `Registration failed: ${e.message}` };
    }
  }

  async createToken(apiKey) {
    const key = apiKey || this.apiKey;
    if (!key) return { error: 'No API key provided' };
    try {
      const resp = await axios.post(`${this.baseUrl}/api/v1/identity/token`, {}, {
        headers: { 'X-API-Key': key },
        timeout: 10000
      });
      return resp.data;
    } catch (e) {
      return { error: `Token creation failed: ${e.message}` };
    }
  }

  async fetchPublicKeyByApiKey(apiKey) {
    const key = apiKey || this.apiKey;
    if (!key) return null;
    try {
      const resp = await axios.get(`${this.baseUrl}/api/v1/keys/public`, {
        params: { api_key: key },
        timeout: 10000
      });
      const data = resp.data;
      if (data.success && data.public_key) {
        return data.public_key;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  async fetchPublicKey(aiId) {
    try {
      const resp = await axios.get(`${this.baseUrl}/api/v1/ai/keys/${aiId}`, { timeout: 10000 });
      const data = resp.data;
      if (data.success && data.public_key) {
        return data.public_key;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  generateKeyPair() {
    const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
      modulusLength: 2048,
      publicKeyEncoding: { type: 'spki', format: 'pem' },
      privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
    });
    return { publicKey, privateKey };
  }

  async generateKeys(aiId, apiKey) {
    const key = apiKey || this.apiKey;
    if (!key) {
      return { success: false, error: 'No API key provided' };
    }

    try {
      const { publicKey, privateKey } = this.generateKeyPair();

      const resp = await axios.post(
        `${this.baseUrl}/api/v1/ai/keys/generate`,
        { ai_id: aiId, public_key: publicKey },
        { headers: { 'X-API-Key': key }, timeout: 10000 }
      );

      const data = resp.data;
      if (data.success) {
        return {
          success: true,
          ai_id: aiId,
          public_key: publicKey,
          private_key: privateKey,
          message: 'Store the private key securely — it cannot be retrieved later.',
        };
      }
      return data;
    } catch (e) {
      return { success: false, error: `Key generation failed: ${e.message}` };
    }
  }

  signRequest(privateKeyPem, message) {
    const sign = crypto.createSign('SHA256');
    sign.update(message);
    sign.end();
    return sign.sign(privateKeyPem, 'base64');
  }

  buildAuthHeaders(privateKeyPem, method = 'GET', path = '/') {
    const timestamp = String(Math.floor(Date.now() / 1000));
    const message = `${method}:${path}:${timestamp}`;
    const signature = this.signRequest(privateKeyPem, message);

    return {
      'X-Agent-Signature': signature,
      'X-Agent-Timestamp': timestamp,
    };
  }

  verifySignatureOffline(publicKeyPem, message, signatureBase64) {
    try {
      const verify = crypto.createVerify('SHA256');
      verify.update(message);
      verify.end();
      return verify.verify(publicKeyPem, signatureBase64, 'base64');
    } catch (e) {
      return false;
    }
  }

  }

function createNexus6Middleware(options = {}) {
  const {
    mode = 'signature',
    excludePaths = ['/health', '/favicon.ico'],
    onVerified = null,
    baseUrl = DEFAULT_BASE_URL,
    signatureMaxAgeSeconds = 300,
  } = options;

  return async function nexus6Middleware(req, res, next) {
    const path = req.url.split('?')[0];
    if (excludePaths.some(p => path.startsWith(p))) {
      return next();
    }

    if (mode === 'signature') {
      return handleSignatureMode(req, res, next, { baseUrl, signatureMaxAgeSeconds, onVerified });
    }

    return handleApiKeyMode(req, res, next, { baseUrl, onVerified });
  };
}

async function handleApiKeyMode(req, res, next, { baseUrl, onVerified }) {
  const apiKey = req.headers['x-api-key'];
  if (!apiKey) {
    return next();
  }

  const client = new Nexus6Client({ baseUrl });
  const result = await client.verify(apiKey);

  if (!result.verified) {
    res.status(401).json({ error: 'Invalid AI identity', details: result.error || '' });
    return;
  }

  req.aiIdentity = result;
  if (onVerified) onVerified(req, result);

  next();
}

const publicKeyCache = new Map();

async function handleSignatureMode(req, res, next, { baseUrl, signatureMaxAgeSeconds, onVerified }) {
  const apiKey = req.headers['x-api-key'];
  const signature = req.headers['x-agent-signature'];
  const timestamp = req.headers['x-agent-timestamp'];

  if (!apiKey) {
    return next();
  }

  if (!signature || !timestamp) {
    res.status(401).json({
      error: 'Missing signature headers',
      details: 'X-Agent-Signature and X-Agent-Timestamp are required when using X-API-Key',
    });
    return;
  }

  const now = Math.floor(Date.now() / 1000);
  const ts = parseInt(timestamp, 10);
  if (isNaN(ts) || Math.abs(now - ts) > signatureMaxAgeSeconds) {
    res.status(401).json({
      error: 'Signature expired',
      details: `Timestamp age exceeds ${signatureMaxAgeSeconds}s limit`,
    });
    return;
  }

  const method = req.method;
  const path = req.url.split('?')[0];
  const message = `${method}:${path}:${timestamp}`;

  let publicKey;
  const cached = publicKeyCache.get(apiKey);
  if (cached && now - cached.cachedAt < 3600) {
    publicKey = cached.key;
  } else {
    const client = new Nexus6Client({ baseUrl });
    publicKey = await client.fetchPublicKeyByApiKey(apiKey);
    if (publicKey) {
      publicKeyCache.set(apiKey, { key: publicKey, cachedAt: now });
    }
  }

  if (!publicKey) {
    res.status(401).json({
      error: 'Invalid AI identity signature',
      details: `Public key not found for API key`,
    });
    return;
  }

  const client = new Nexus6Client({ baseUrl });
  const isValid = client.verifySignatureOffline(publicKey, message, signature);

  if (!isValid) {
    res.status(401).json({
      error: 'Invalid AI identity signature',
      details: 'RSA signature verification failed',
    });
    return;
  }

  req.aiIdentity = { verified: true, identity: { api_key: apiKey, verified_by: 'rsa-signature' } };
  if (onVerified) onVerified(req, req.aiIdentity);

  next();
}

module.exports = { Nexus6Client, createNexus6Middleware };