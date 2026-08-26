#!/usr/bin/env python3
"""Container health check using a direct loopback connection (no proxy lookup)."""

from http.client import HTTPConnection
import os


connection = HTTPConnection("127.0.0.1", int(os.environ.get("SERVICE_PORT", "8080")), timeout=2)
try:
    connection.request("GET", "/health")
    response = connection.getresponse()
    response.read()
    raise SystemExit(0 if response.status == 200 else 1)
finally:
    connection.close()

