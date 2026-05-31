/**
 * Anexus + Express.js: Platform-side auth code verification middleware.
 *
 * Run:
 *   npm init -y
 *   npm install express node-fetch
 *   node examples/javascript/express_middleware.js
 *
 * Test:
 *   curl -X POST http://localhost:3000/api/ai-action \
 *     -H "Content-Type: application/json" \
 *     -d '{"auth_code": "anx://shopify/user_abc123?exp=3600&ts=1717000000"}'
 */

const express = require("express");

// In production, use a real fetch. For Node 18+, fetch is built-in.
const fetch = require("node-fetch");

const app = express();
app.use(express.json());

// Get your API Key from the Anexus Dashboard
const API_KEY = "nxs6_xxxxxxxxxxxx";
const ANEXUS_API = "http://localhost:8000";

/**
 * Middleware: verify an Anexus auth code before processing the request.
 */
async function verifyAnexusCode(req, res, next) {
  const authCode = req.headers["x-auth-code"] || req.body?.auth_code;

  if (!authCode) {
    return res.status(400).json({ error: "Missing auth code" });
  }

  try {
    const response = await fetch(`${ANEXUS_API}/api/v1/codes/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: authCode, api_key: API_KEY }),
    });

    const result = await response.json();

    if (!result.verified) {
      return res.status(403).json({
        error: result.error || "Invalid auth code",
      });
    }

    // Attach verified user info to the request
    req.user = {
      username: result.username,
      userId: result.user_id,
      permissions: result.permissions || [],
    };

    next();
  } catch (err) {
    console.error("Verification error:", err);
    return res.status(500).json({ error: "Verification service unavailable" });
  }
}

// Protected route — uses the middleware to verify the auth code
app.post("/api/ai-action", verifyAnexusCode, (req, res) => {
  // req.user is set by the middleware after successful verification
  res.json({
    access: "granted",
    user: req.user.username,
    can: req.user.permissions,
  });
});

app.listen(3000, () => {
  console.log("Express platform server on http://localhost:3000");
  console.log("Auth codes verified via Anexus middleware");
});