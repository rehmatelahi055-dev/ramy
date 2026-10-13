#!/usr/bin/env python3
from __future__ import annotations

import os

os.environ.setdefault("BOT_MODE", "PAPER")
os.environ.setdefault("LIVE_ENABLED", "false")

from ramy.engine import main

if __name__ == "__main__":
    main()
