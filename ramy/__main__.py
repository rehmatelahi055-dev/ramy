from __future__ import annotations

import argparse
import os
from typing import Optional

from .config import BotConfig, TradingMode


def main() -> None:
    parser = argparse.ArgumentParser(description="ramy Binance Futures bot")
    parser.add_argument("--mode", choices=[m.value for m in TradingMode], default="PAPER")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    mode = TradingMode(args.mode)
    if args.live:
        os.environ["LIVE_ENABLED"] = "true"
    config = BotConfig.from_env()
    config.mode = mode
    if mode == TradingMode.LIVE and not config.live_enabled:
        raise ValueError("LIVE mode is disabled until explicit confirmation is provided.")

    print(f"ramy booted in {config.mode.value} mode.")
    print("This project is configured conservatively and blocks unsafe live entries by default.")


if __name__ == "__main__":
    main()
