#!/usr/bin/env python3
"""Set a demo service's state using an exact allowlist."""

from __future__ import annotations

import os
import sys
from pathlib import Path


ALLOWED_STATES = {"healthy", "degraded"}
STATE_FILE = Path(os.environ.get("STATE_FILE", "/state/status"))


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in ALLOWED_STATES:
        print("Usage: statectl.py {healthy|degraded}", file=sys.stderr)
        return 2

    state = sys.argv[1]
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(f"{state}\n", encoding="utf-8")
    os.replace(temporary, STATE_FILE)
    print(state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

