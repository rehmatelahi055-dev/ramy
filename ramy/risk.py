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
    max_quantity_by_margin: Decimal
    passes: bool
    reasons: List[str]
    margin_required: Decimal


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
        invest_per_trade = invest_per_trade or self.config.invest_per_trade
        cap_total_investment = cap_total_investment or self.config.cap_total_investment

        if equity <= 0:
            reasons.append("Equity must be positive.")

        stop_distance = abs(entry_price - stop_loss)
        if stop_distance <= 0:
            reasons.append("Stop distance must be positive.")

        # Fixed allocation per trade for spot
        position_notional = invest_per_trade
        quantity = (position_notional / entry_price) if entry_price > 0 else Decimal("0")

        # simple min notional check
        if position_notional < Decimal("1"):
            reasons.append("Invest per trade below minimum notional.")

        # capacity check
        if len(current_positions) >= self.config.max_concurrent_positions:
            reasons.append("Maximum concurrent positions reached.")

        # cap check
        aggregate_invested = sum((pos.get("notional", Decimal("0")) for pos in current_positions), Decimal("0"))
        if aggregate_invested + position_notional > cap_total_investment:
            reasons.append("Cap total investment would be exceeded.")

        # risk budget vs stop-distance
        risk_budget = self.current_risk_budget(equity)
        estimated_loss_if_hit = stop_distance * quantity
        if estimated_loss_if_hit > risk_budget:
            reasons.append("Estimated loss exceeds configured risk budget.")

        passes = not reasons
        margin_required = position_notional
        return RiskOutcome(
            allowed_risk_usdt=risk_budget,
            stop_distance=stop_distance,
            loss_per_unit=stop_distance,
            quantity=quantity,
            max_quantity_by_margin=quantity,
            passes=passes,
            reasons=reasons,
            margin_required=margin_required,
        )

    def normalize_quantity(self, quantity: Decimal, step_size: Decimal = Decimal("0.000001")) -> Decimal:
        q = (quantity.quantize(step_size, rounding=ROUND_HALF_UP))
        return q if q > 0 else Decimal("0")

    def enforce_limits(self, quantity: Decimal, price: Decimal, stop_loss: Decimal, side: str, equity: Decimal) -> bool:
        outcome = self.calculate_trade_risk(equity=equity, current_positions=[], entry_price=price, stop_loss=stop_loss, side=side)
        if not outcome.passes:
            return False
        if quantity <= 0:
            return False
        if quantity > outcome.quantity:
            return False
        return True


def compute_position_notional(entry_price: Decimal, quantity: Decimal) -> Decimal:
    return entry_price * quantity
