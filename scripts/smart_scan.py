from __future__ import annotations

from typing import List

from .config import BotConfig
from .engine import build_symbol_prices
from .scanner import SmartScanner


def run_scan_print() -> None:
    cfg = BotConfig.from_env()
    scanner = SmartScanner(cfg)
    prices = build_symbol_prices()
    candidates = scanner.scan(prices)
    print(f"Found {len(candidates)} candidates")
    for c in candidates:
        print(f"{c['symbol']} score={c['score']:.1f} entry={c['entry']:.6f} stop={c['stop']:.6f} tp={c['target']:.6f}")


if __name__ == "__main__":
    run_scan_print()
