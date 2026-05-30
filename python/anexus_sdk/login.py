"""Anexus Login CLI — automated browser-based login (GitHub Copilot style).
Usage:
    python -m anexus_sdk.login

Opens browser → user logs in → automatically captures session token → saves to ~/.anexus/token
No manual copy/paste needed.
"""

import sys, os, json, socket, threading, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

TOKEN_DIR = os.path.expanduser("~/.anexus")
TOKEN_PATH = os.path.join(TOKEN_DIR, "token")
AUTH_URL = os.environ.get("ANEXUS_AUTH_URL", "http://localhost:8000/auth")


def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main():
    port = find_free_port()
    callback_url = f"http://127.0.0.1:{port}"
    auth_url = f"{AUTH_URL}?redirect={callback_url}"

    result = {"token": None}

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            params = parse_qs(urlparse(self.path).query)
            token = params.get("session_token", [None])[0]
            if token:
                result["token"] = token
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    "<!DOCTYPE html><html><body style='background:#09090b;color:#fafafa;font-family:sans-serif;"
                    "display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0'>"
                    "<div style='text-align:center'><h1 style='font-size:24px'>Authenticated!</h1>"
                    "<p style='color:#a1a1aa;margin-top:8px'>You can close this window and return to your terminal.</p>"
                    "</div></body></html>".encode()
                )
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing session_token")
            # Shutdown server in a separate thread
            threading.Thread(target=server.shutdown, daemon=True).start()

        def log_message(self, *a):
            pass  # silent

    server = HTTPServer(("127.0.0.1", port), CallbackHandler)

    print("")
    print("  Opening browser for Anexus login...")
    print("")

    webbrowser.open(auth_url)

    server.serve_forever()

    token = result["token"]
    if not token:
        print("  ✗ Login failed or cancelled")
        sys.exit(1)

    os.makedirs(TOKEN_DIR, exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        f.write(token)

    print(f"  ✓ Logged in successfully")
    print(f"  Token saved to ~/.anexus/token")
    print("")


if __name__ == "__main__":
    main()