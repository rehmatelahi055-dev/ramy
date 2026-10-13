from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional

from .config import BotConfig


@dataclass
class PaperFill:
    symbol: str
    side: str
    order_type: str
    price: Decimal
    quantity: Decimal
    fees: Decimal
    pnl: Decimal


class SpotAdapter:
    """Simple adapter that validates orders and simulates spot behavior in PAPER mode.

    This adapter does not call Binance. It is safe for unit tests and local runs.
    Replace with a real exchange adapter using python-binance or direct REST calls for Testnet/LIVE.
    """

    def __init__(self, config: BotConfig) -> None:
        self.config = config

    def preflight_checks(self) -> Dict[str, Any]:
        checks = {"mode": self.config.mode.value, "ok": True, "warnings": []}
        if self.config.mode == "LIVE" and not self.config.live_enabled:
            checks["ok"] = False
            checks["warnings"].append("LIVE mode disabled")
        if self.config.mode == BotConfig().mode and not self.config.api_key:
            # PAPER default: no keys required
            pass
        return checks

    def validate_filters(self, symbol: str, quantity: Decimal, price: Decimal, min_notional: Decimal = Decimal("10")) -> bool:
        if quantity <= 0:
            return False
        if price <= 0:
            return False
        if symbol.strip() == "":
            return False
        notional = quantity * price
        if notional < min_notional:
            # Binance spot min notional often 10 USDT (varies by symbol)
            return False
        return True

    def submit_limit_buy(self, symbol: str, price: Decimal, quantity: Decimal) -> Dict[str, Any]:
        if not self.validate_filters(symbol, quantity, price):
            return {"accepted": False, "reason": "Invalid order filters."}
        # Simulate pending order
        client_oid = f"paper-{symbol}-limit-{abs(hash(symbol+str(price))) }"
        return {"accepted": True, "status": "NEW", "client_order_id": client_oid, "price": str(price), "quantity": str(quantity)}

    def submit_oco(self, symbol: str, side: str, quantity: Decimal, price: Decimal, stop_price: Decimal, stop_limit_price: Decimal) -> Dict[str, Any]:
        # OCO parameters: price (limit take-profit), stopPrice (trigger), stopLimitPrice (limit price)
        if not self.validate_filters(symbol, quantity, price, min_notional=Decimal("1")):
            return {"accepted": False, "reason": "Invalid OCO filters."}
        client_oid = f"paper-{symbol}-oco-{abs(hash(symbol+str(price)+str(stop_price))) }"
        return {"accepted": True, "status": "OCO_PLACED", "client_order_id": client_oid}

    def cancel_order(self, symbol: str, client_order_id: str) -> Dict[str, Any]:
        return {"canceled": True, "client_order_id": client_order_id}

    def get_position(self, symbol: str) -> Dict[str, Any]:
        # Placeholder for actual exchange read
        return {"symbol": symbol, "quantity": Decimal("0"), "side": "NONE"}

    def reconcile_orders(self) -> Dict[str, Any]:
        return {"status": "OK", "open_orders": 0}
