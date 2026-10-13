from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional


@dataclass
class SimulatedTrade:
    symbol: str
    side: str
    entry_price: Decimal
    quantity: Decimal
    fee_rate: Decimal = Decimal("0.0006")
    slippage: Decimal = Decimal("0.0005")

    def fill(self) -> Dict[str, Any]:
        gross = self.quantity * self.entry_price
        fees = gross * self.fee_rate
        slippage_cost = gross * self.slippage
        pnl = Decimal("0")
        return {
            "symbol": self.symbol,
            "side": self.side,
            "entry_price": self.entry_price,
            "quantity": self.quantity,
            "fees": fees,
            "slippage_cost": slippage_cost,
            "pnl": pnl,
        }
