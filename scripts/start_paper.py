#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
import sys


def main() -> None:
    os.environ.setdefault("BOT_MODE", "PAPER")
    os.environ.setdefault("LIVE_ENABLED", "false")
    subprocess.run([sys.executable, "-m", "ramy", "--mode", "PAPER"], check=True)


if __name__ == "__main__":
    main()
