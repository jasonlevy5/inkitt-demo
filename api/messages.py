from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error
import ssl

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")

        if not api_key:
            self._send(500, {"error": "ANTHROPIC_API_KEY not configured"})
            return

        req = urllib.request.Request(
            ANTHROPIC_URL,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )

        ctx = ssl.create_default_context()

        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                resp_body = resp.read()
                self._send(resp.status, json.loads(resp_body))
        except urllib.error.HTTPError as e:
            err_body = e.read()
            try:
                self._send(e.code, json.loads(err_body))
            except Exception:
                self._send(e.code, {"error": err_body.decode()})
        except Exception as e:
            self._send(500, {"error": str(e)})

    def _send(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
