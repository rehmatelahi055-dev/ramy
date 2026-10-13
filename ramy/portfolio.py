from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

from .config import BotConfig


@dataclass
class PositionSnapshot:
    symbol: str
    side: str
    quantity: Decimal
    entry_price: Decimal
    mark_price: Decimal
    unrealized_pnl: Decimal
    margin: Decimal


class PortfolioManager:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.positions: Dict[str, PositionSnapshot] = {}

    def add_position(self, snapshot: PositionSnapshot) -> None:
        self.positions[snapshot.symbol] = snapshot

    def remove_position(self, symbol: str) -> None:
        self.positions.pop(symbol, None)

    def aggregate_margin(self) -> Decimal:
        return sum((p.margin for p in self.positions.values()), Decimal("0"))

    def current_equity(self, balance: Decimal) -> Decimal:
        return balance + sum((p.unrealized_pnl for p in self.positions.values()), Decimal("0"))

    def pos_count(self) -> int:
        return len(self.positions)

    def risk_exceeded(self, projected_margin: Decimal) -> bool:
        return self.aggregate_margin() + projected_margin > (self.config.starting_equity * self.config.max_aggregate_initial_margin_percent / Decimal("100"))
