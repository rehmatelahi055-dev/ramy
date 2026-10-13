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
        max_margin_per_trade: Optional[Decimal] = None,
        max_positions: Optional[int] = None,
        aggregate_margin_limit: Optional[Decimal] = None,
    ) -> RiskOutcome:
        reasons: List[str] = []
        max_positions = max_positions or self.config.max_concurrent_positions
        aggregate_margin_limit = aggregate_margin_limit or (
            self.config.starting_equity * self.config.max_aggregate_initial_margin_percent / Decimal("100")
        )
        max_margin_per_trade = max_margin_per_trade or self.config.max_initial_margin_per_position

        if equity <= 0:
            reasons.append("Equity must be positive.")

        if side == "LONG":
            stop_distance = max(Decimal("0"), entry_price - stop_loss)
        elif side == "SHORT":
            stop_distance = max(Decimal("0"), stop_loss - entry_price)
        else:
            stop_distance = Decimal("0")
            reasons.append("Trade side must be LONG or SHORT.")

        if stop_distance <= 0:
            reasons.append("Stop distance must be positive.")

        risk_budget = self.current_risk_budget(equity)
        if risk_budget <= 0:
            reasons.append("Risk budget is zero or negative.")

        loss_per_unit = stop_distance
        quantity_by_risk = risk_budget / loss_per_unit if loss_per_unit > 0 else Decimal("0")
        position_margin = (quantity_by_risk * entry_price) / self.config.default_leverage
        margin_required = position_margin

        if len(current_positions) >= max_positions:
            reasons.append("Maximum concurrent positions reached.")

        if margin_required > max_margin_per_trade:
            reasons.append("Required margin exceeds the per-position cap.")

        aggregate_margin = sum((pos.get("margin", Decimal("0")) for pos in current_positions), Decimal("0"))
        if aggregate_margin + margin_required > aggregate_margin_limit:
            reasons.append("Aggregate margin limit would be exceeded.")

        quantity = quantity_by_risk
        if quantity <= 0:
            reasons.append("Calculated quantity is not positive.")

        passes = not reasons
        return RiskOutcome(
            allowed_risk_usdt=risk_budget,
            stop_distance=stop_distance,
            loss_per_unit=loss_per_unit,
            quantity=quantity,
            max_quantity_by_margin=quantity_by_risk,
            passes=passes,
            reasons=reasons,
            margin_required=margin_required,
        )

    def normalize_quantity(self, quantity: Decimal, tick_size: Decimal = Decimal("0.001")) -> Decimal:
        q = quantity.quantize(tick_size, rounding=ROUND_HALF_UP)
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


def compute_position_margin(entry_price: Decimal, quantity: Decimal, leverage: Decimal) -> Decimal:
    return (entry_price * quantity) / leverage
