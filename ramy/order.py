from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional

from .config import BotConfig


@dataclass
class RiskOutcome:
    allowed_risk_usdt: Decimal
    stop_distance: Decimal
    loss_per_unit: Decimal
    quantity: Decimal
    passes: bool
    reasons: List[str]
    notional: Decimal


class RiskEngine:
    def __init__(self, config: BotConfig) -> None:
        self.config = config

    def current_risk_budget(self, equity: Decimal) -> Decimal:
        return (equity * self.config.risk_per_trade_percent) / Decimal("100")

    def calculate_trade_risk(
        self,
        equity: Decimal,
        current_positions: List[Dict[str, Decimal]],
        entry_price: Decimal,
        stop_loss: Decimal,
        side: str,
        invest_per_trade: Optional[Decimal] = None,
        cap_total_investment: Optional[Decimal] = None,
    ) -> RiskOutcome:
        reasons: List[str] = []
        invest = invest_per_trade or self.config.invest_per_trade
        cap = cap_total_investment or self.config.cap_total_investment
        if equity <= 0:
            reasons.append("Equity must be positive.")

        if entry_price <= 0:
            reasons.append("Entry price must be positive.")

        stop_distance = abs(entry_price - stop_loss)
        if stop_distance <= 0:
            reasons.append("Stop distance must be positive.")

        qty = invest / entry_price if entry_price > 0 else Decimal("0")
        estimated_loss = qty * stop_distance
        risk_budget = self.current_risk_budget(equity)
        if estimated_loss > risk_budget:
            reasons.append("Estimated loss exceeds configured risk budget.")

        if len(current_positions) >= self.config.max_concurrent_positions:
            reasons.append("Maximum concurrent positions reached.")

        aggregate_invested = sum((pos.get("notional", Decimal("0")) for pos in current_positions), Decimal("0"))
        if aggregate_invested + invest > cap:
            reasons.append("Aggregate investment would exceed the total cap.")

        outcome = RiskOutcome(
            allowed_risk_usdt=risk_budget,
            stop_distance=stop_distance,
            loss_per_unit=stop_distance,
            quantity=qty,
            passes=not reasons,
            reasons=reasons,
            notional=invest,
        )
        return outcome

    def normalize_quantity(self, quantity: Decimal, tick_size: Decimal = Decimal("0.000001")) -> Decimal:
        q = quantity.quantize(tick_size, rounding=ROUND_HALF_UP)
        return q if q > 0 else Decimal("0")

    def enforce_limits(self, quantity: Decimal, price: Decimal, stop_loss: Decimal, side: str, equity: Decimal) -> bool:
        result = self.calculate_trade_risk(
            equity=equity,
            current_positions=[],
            entry_price=price,
            stop_loss=stop_loss,
            side=side,
        )
        return result.passes and quantity > 0 and quantity <= result.quantity
