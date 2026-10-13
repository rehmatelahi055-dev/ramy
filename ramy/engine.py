from __future__ import annotations

from decimal import Decimal
from typing import Iterable, List

from .config import BotConfig
from .market_data import Candle, candles_from_series
from .strategy import StrategyEngine


class SymbolScanner:
    def __init__(self, config: BotConfig, strategy: StrategyEngine | None = None) -> None:
        self.config = config
        self.strategy = strategy or StrategyEngine(config)

    def _base_symbol_list(self) -> list[str]:
        return [
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
            "BNBUSDT",
            "XRPUSDT",
            "ADAUSDT",
            "DOGEUSDT",
            "LINKUSDT",
            "AVAXUSDT",
            "MATICUSDT",
        ]

    def scan(self, symbol_prices: dict[str, list[float]]) -> List[dict]:
        candidates: List[dict] = []
        for symbol, series in symbol_prices.items():
            candles = [c.__dict__ for c in candles_from_series(series, length=len(series))]
            signal = self.strategy.generate_signal(symbol, candles)
            if signal is not None:
                candidates.append({
                    "symbol": symbol,
                    "side": signal.side,
                    "score": str(signal.score),
                    "entry": str(signal.entry_price),
                    "stop": str(signal.stop_loss),
                    "target": str(signal.take_profit),
                })
        return sorted(candidates, key=lambda item: float(item["score"]), reverse=True)[0:self.config.max_symbol_scan_batch]


def build_symbol_prices() -> dict[str, list[float]]:
    prices: dict[str, list[float]] = {}
    base = 100.0
    for idx, symbol in enumerate([
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
        "BNBUSDT",
        "XRPUSDT",
        "ADAUSDT",
        "DOGEUSDT",
        "LINKUSDT",
        "AVAXUSDT",
        "MATICUSDT",
    ]):
        trend = 1.002 + (idx * 0.0004)
        series: list[float] = []
        value = base
        for step in range(150):
            value = value * trend
            series.append(value)
        prices[symbol] = series
    return prices
