#!/usr/bin/env python3
"""Small HTTP service for the UiPath health-monitor demonstration."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


ALLOWED_SERVICES = {"demo-alpha", "demo-beta", "demo-gamma"}
ALLOWED_STATES = {"healthy", "degraded"}
SERVICE_NAME = os.environ.get("SERVICE_NAME", "")
PORT = int(os.environ.get("SERVICE_PORT", "8080"))
STATE_FILE = Path(os.environ.get("STATE_FILE", "/state/status"))

if SERVICE_NAME not in ALLOWED_SERVICES:
    raise SystemExit(f"Invalid SERVICE_NAME: {SERVICE_NAME!r}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_state() -> str:
    try:
        state = STATE_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text("healthy\n", encoding="utf-8")
        return "healthy"
    return state if state in ALLOWED_STATES else "degraded"


class Handler(BaseHTTPRequestHandler):
    server_version = "UiPathDemoHealth/1.0"

    def do_GET(self) -> None:  # noqa: N802 - HTTP method name
        path = urlsplit(self.path).path
        state = read_state()

        if path == "/health":
            degraded = state == "degraded"
            self.send_json(
                503 if degraded else 200,
                {
                    "service": SERVICE_NAME,
                    "status": state,
                    "timestampUtc": utc_now(),
                    "responseTimeMs": 1500 if degraded else 12,
                    "dependency": "unavailable" if degraded else "connected",
                    "message": "Simulated dependency failure" if degraded else "All checks passed",
                },
            )
            return

        if path == "/metrics":
            degraded = state == "degraded"
            self.send_json(
                200,
                {
                    "service": SERVICE_NAME,
                    "timestampUtc": utc_now(),
                    "simulated": True,
                    "cpuPercent": 91.3 if degraded else 18.4,
                    "memoryPercent": 84.2 if degraded else 42.1,
                    "diskPercent": 31.7,
                    "errorCount": 7 if degraded else 0,
                },
            )
            return

        if path == "/diagnostics":
            self.send_json(
                200,
                {
                    "service": SERVICE_NAME,
                    "state": state,
                    "timestampUtc": utc_now(),
                    "checks": {
                        "application": "running",
                        "dependency": "simulated-unavailable" if state == "degraded" else "connected",
                    },
                },
            )
            return

        self.send_json(404, {"error": "not_found", "message": "Unknown endpoint"})

    def send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string: str, *args: object) -> None:
        print(f"{utc_now()} {self.address_string()} {format_string % args}", flush=True)


if __name__ == "__main__":
    read_state()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"{SERVICE_NAME} listening on container port {PORT}", flush=True)
    server.serve_forever()

