#!/usr/bin/env python3
"""
Tiny proxy server for The Millennium Wolves.
Serves index.html and proxies /api/messages to the Anthropic API.

Usage:
    python3 server.py
    Then open http://localhost:8080
"""

import http.server
import json
import os
import urllib.request
import urllib.error
import ssl

PORT = 8080
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
DIR = os.path.dirname(os.path.abspath(__file__))

# Load API key from .env file
def load_api_key():
    env_path = os.path.join(DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip().startswith("ANTHROPIC_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return os.environ.get("ANTHROPIC_API_KEY", "")

API_KEY = load_api_key()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_POST(self):
        if self.path != "/api/messages":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        req = urllib.request.Request(
            ANTHROPIC_URL,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )

        ctx = ssl.create_default_context()

        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            err_body = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(err_body)

    def log_message(self, format, *args):
        print(f"  {args[0]}" if args else "")


if __name__ == "__main__":
    server = http.server.HTTPServer(("", PORT), Handler)
    print(f"\n  The Millennium Wolves")
    print(f"  ─────────────────────")
    print(f"  Running at http://localhost:{PORT}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        server.server_close()
