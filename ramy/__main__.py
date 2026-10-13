from __future__ import annotations

import argparse
import os
from decimal import Decimal

from .config import BotConfig
from .engine import BotEngine
from .exchange import BinanceSpotAdapter
from .scanner import SmartScanner


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=os.getenv("BOT_MODE", "PAPER"))
    args = parser.parse_args()

    cfg = BotConfig.from_env()

    print("Starting smart scan...")
    scanner = SmartScanner(cfg)
    prices = BotEngine(cfg).run_scan()  # reuse generated prices
    print("Top candidates:")
    for c in prices:
        print(c)

    # Example Testnet preflight
    if cfg.mode.name == "BINANCE_TESTNET":
        adapter = BinanceSpotAdapter(cfg.testnet_api_key, cfg.testnet_api_secret, testnet=True)
        pre = adapter.connect()
        print(f"Testnet preflight: {pre}")


if __name__ == "__main__":
    main()
