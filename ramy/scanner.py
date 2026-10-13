from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional

from .config import BotConfig


@dataclass
class SpotFill:
    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Decimal
    fee: Decimal = Decimal("0")
    pnl: Decimal = Decimal("0")


class SpotAdapter:
    def __init__(self, config: BotConfig) -> None:
        self.config = config

    def preflight_checks(self) -> Dict[str, Any]:
        return {
            "mode": self.config.mode.value,
            "ok": True,
            "warnings": [],
            "live_disabled": not self.config.live_enabled,
        }

    def validate_filters(self, symbol: str, quantity: Decimal, price: Decimal, min_notional: Decimal = Decimal("10")) -> bool:
        if not symbol or not symbol.strip():
            return False
        if quantity <= 0:
            return False
        if price <= 0:
            return False
        if quantity * price < min_notional:
            return False
        return True

    def submit_limit_buy(self, symbol: str, price: Decimal, quantity: Decimal) -> Dict[str, Any]:
        if not self.validate_filters(symbol, quantity, price):
            return {"accepted": False, "reason": "Invalid buy order."}
        client_id = f"paper-{symbol}-buy-{abs(hash(symbol + str(price) + str(quantity)))}"
        return {
            "accepted": True,
            "status": "NEW",
            "client_order_id": client_id,
            "order_type": "LIMIT_BUY",
            "price": str(price),
            "quantity": str(quantity),
        }

    def submit_oco(self, symbol: str, side: str, quantity: Decimal, price: Decimal, stop_price: Decimal, stop_limit_price: Decimal) -> Dict[str, Any]:
        if side.upper() not in {"BUY", "SELL"}:
            return {"accepted": False, "reason": "Side must be BUY or SELL."}
        if not self.validate_filters(symbol, quantity, price, Decimal("1")):
            return {"accepted": False, "reason": "Invalid OCO parameters."}
        client_id = f"paper-{symbol}-oco-{abs(hash(symbol + str(price) + str(stop_price)))}"
        return {
            "accepted": True,
            "status": "OCO_PLACED",
            "client_order_id": client_id,
            "side": side.upper(),
            "limit_price": str(price),
            "stop_price": str(stop_price),
            "stop_limit_price": str(stop_limit_price),
        }

    def cancel_order(self, symbol: str, client_order_id: str) -> Dict[str, Any]:
        return {"accepted": True, "symbol": symbol, "client_order_id": client_order_id, "status": "CANCELED"}

    def reconcile_orders(self) -> Dict[str, Any]:
        return {"status": "OK", "open_orders": 0}
