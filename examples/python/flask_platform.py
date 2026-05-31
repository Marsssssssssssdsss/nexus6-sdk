"""Anexus + Flask: Platform-side auth code verification.

Run:
    pip install anexus-verify flask
    python examples/python/flask_platform.py

Test:
    curl -X POST http://localhost:5000/api/ai-action \
      -H "Content-Type: application/json" \
      -d '{"auth_code": "anx://shopify/user_abc123?exp=3600&ts=1717000000"}'
"""

from flask import Flask, request, jsonify
from anexus_verify import verify_code

app = Flask(__name__)

# Get your API Key from the Anexus Dashboard
API_KEY = "nxs6_xxxxxxxxxxxx"


@app.route("/api/ai-action", methods=["POST"])
def handle_ai_request():
    """
    Called when a user's AI agent sends an Anexus auth code.
    The AI wants to perform an action on behalf of a human user.
    """
    data = request.get_json()
    auth_code = data.get("auth_code")

    if not auth_code:
        return jsonify({"error": "Missing auth_code"}), 400

    # Verify the code with Anexus
    result = verify_code(code=auth_code, api_key=API_KEY)

    if not result.get("verified"):
        return jsonify({"error": result.get("error", "Invalid auth code")}), 403

    # Code is valid — we know who this user is
    username = result["username"]
    user_id = result["user_id"]
    permissions = result.get("permissions", [])

    print(f"  Verified: {username} ({user_id})")
    print(f"  Permissions: {permissions}")

    # Grant access based on verified identity
    return jsonify({
        "access": "granted",
        "user": username,
        "can": permissions,
    })


if __name__ == "__main__":
    print("Flask platform server running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)