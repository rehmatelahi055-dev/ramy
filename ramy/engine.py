from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from .config import BotConfig, TradingMode
from .market_data import MarketDataStore
from .risk import RiskEngine
from .strategy import SignalCandidate, StrategyEngine


@dataclass
class BotSnapshot:
    mode: TradingMode
    equity: Decimal
    balance: Decimal
    open_positions: int
    active_circuit_breakers: int


class BotEngine:
    def __init__(self, config: BotConfig, market_data: Optional[MarketDataStore] = None) -> None:
        self.config = config
        self.market_data = market_data or MarketDataStore()
        self.strategy = StrategyEngine(config)
        self.risk = RiskEngine(config)

    def scan_symbol(self, symbol: str, candles: list[dict]) -> Optional[SignalCandidate]:
        if self.config.mode == TradingMode.LIVE:
            return None
        return self.strategy.generate_signal(symbol, candles)

    def run_cycle(self, symbol: str, candles: list[dict], balance: Decimal, positions: list[dict]) -> Optional[SignalCandidate]:
        signal = self.scan_symbol(symbol, candles)
        if signal is None:
            return None
        risk = self.risk.calculate_trade_risk(
            equity=balance,
            current_positions=positions,
            entry_price=signal.entry_price or Decimal("1"),
            stop_loss=signal.stop_loss or Decimal("1"),
            side=signal.side,
        )
        if not risk.passes:
            return None
        return signal

    def snapshot(self, balance: Decimal, open_positions: int, circuit_breakers: int) -> BotSnapshot:
        return BotSnapshot(
            mode=self.config.mode,
            equity=balance,
            balance=balance,
            open_positions=open_positions,
            active_circuit_breakers=circuit_breakers,
        )
