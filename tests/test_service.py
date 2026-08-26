#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]


class DemoServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.state_file = Path(self.tempdir.name) / "status"
        self.port = 18991
        environment = os.environ.copy()
        environment.update(
            SERVICE_NAME="demo-beta",
            SERVICE_PORT=str(self.port),
            STATE_FILE=str(self.state_file),
        )
        self.process = subprocess.Popen(
            [sys.executable, str(ROOT / "app/server.py")],
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(40):
            try:
                urlopen(f"http://127.0.0.1:{self.port}/health", timeout=0.2).close()
                break
            except Exception:
                time.sleep(0.05)
        else:
            self.fail("demo service did not start")

    def tearDown(self) -> None:
        self.process.terminate()
        self.process.wait(timeout=3)
        self.tempdir.cleanup()

    def get_json(self, path: str) -> tuple[int, dict[str, object]]:
        try:
            response = urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=2)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.loads(response.read())

    def set_state(self, state: str) -> None:
        environment = os.environ.copy()
        environment["STATE_FILE"] = str(self.state_file)
        subprocess.run(
            [sys.executable, str(ROOT / "app/statectl.py"), state],
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_healthy_degraded_and_recovered(self) -> None:
        status, body = self.get_json("/health")
        self.assertEqual(200, status)
        self.assertEqual("healthy", body["status"])

        self.set_state("degraded")
        status, body = self.get_json("/health")
        self.assertEqual(503, status)
        self.assertEqual("degraded", body["status"])

        status, metrics = self.get_json("/metrics")
        self.assertEqual(200, status)
        self.assertTrue(metrics["simulated"])
        self.assertGreater(metrics["cpuPercent"], 90)

        self.set_state("healthy")
        status, body = self.get_json("/health")
        self.assertEqual(200, status)
        self.assertEqual("healthy", body["status"])

    def test_unknown_endpoint(self) -> None:
        status, body = self.get_json("/not-an-endpoint")
        self.assertEqual(404, status)
        self.assertEqual("not_found", body["error"])


if __name__ == "__main__":
    unittest.main()
