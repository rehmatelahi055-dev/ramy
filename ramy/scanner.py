from __future__ import annotations

from decimal import Decimal
from typing import List

from .config import BotConfig
from .engine import build_symbol_prices
from .intel import score_candidate
from .strategy import StrategyEngine


class SmartScanner:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.strategy = StrategyEngine(config)

    def scan(self, symbol_prices: dict[str, List[float]]) -> list[dict]:
        candidates = []
        for symbol, series in symbol_prices.items():
            # build candle list similar to previous helper
            candles = []
            for i, price in enumerate(series):
                candles.append([
                    i * 300000,
                    price * 0.99,
                    price * 1.02,
                    price * 0.985,
                    price,
                    1000.0,
                    (i + 1) * 300000,
                ])
            signal = self.strategy.generate_signal(symbol, candles)
            if signal:
                s = score_candidate(symbol, candles)
                candidates.append({
                    "symbol": symbol,
                    "side": signal.side,
                    "score": s,
                    "entry": float(signal.entry_price or Decimal("0")),
                    "stop": float(signal.stop_loss or Decimal("0")),
                    "target": float(signal.take_profit or Decimal("0")),
                })
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[: self.config.max_symbol_scan_batch]
