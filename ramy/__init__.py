from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from .config import BotConfig, TradingMode
from .market_data import MarketDataStore
from .risk import RiskEngine
from .scanner import SymbolScanner, build_symbol_prices
from .strategy import StrategyEngine


@dataclass
class BotSnapshot:
    mode: TradingMode
    equity: Decimal
    open_positions: int
    active_circuit_breakers: int
    candidates: int


class BotEngine:
    def __init__(self, config: BotConfig, market_data: Optional[MarketDataStore] = None) -> None:
        self.config = config
        self.market_data = market_data or MarketDataStore()
        self.strategy = StrategyEngine(config)
        self.risk = RiskEngine(config)
        self.scanner = SymbolScanner(config, self.strategy)

    def run_scan(self) -> list[dict]:
        symbol_prices = build_symbol_prices()
        return self.scanner.scan(symbol_prices)

    def snapshot(self, equity: Decimal, open_positions: int, circuit_breakers: int, candidates: int) -> BotSnapshot:
        return BotSnapshot(
            mode=self.config.mode,
            equity=equity,
            open_positions=open_positions,
            active_circuit_breakers=circuit_breakers,
            candidates=candidates,
        )


def main() -> None:
    config = BotConfig.from_env()
    engine = BotEngine(config)
    results = engine.run_scan()
    print(f"mode={config.mode.value} candidates={len(results)}")
    for item in results:
        print(item)


if __name__ == "__main__":
    main()
