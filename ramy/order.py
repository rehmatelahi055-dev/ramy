from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional

from .config import BotConfig, TradingMode


@dataclass
class PaperFill:
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    fees: Decimal
    pnl: Decimal


class BinanceFuturesAdapter:
    def __init__(self, config: BotConfig) -> None:
        self.config = config

    def preflight_checks(self) -> Dict[str, Any]:
        checks = {
            "mode": self.config.mode.value,
            "live_disabled": not self.config.live_enabled,
            "ok": True,
            "warnings": [],
        }
        if self.config.mode == TradingMode.LIVE and not self.config.live_enabled:
            checks["ok"] = False
            checks["warnings"].append("LIVE mode is disabled by policy.")
        if self.config.mode == TradingMode.LIVE and not self.config.api_key:
            checks["ok"] = False
            checks["warnings"].append("Missing production API credentials.")
        if self.config.mode == TradingMode.BINANCE_FUTURES_TESTNET and not self.config.testnet_api_key:
            checks["ok"] = False
            checks["warnings"].append("Missing testnet credentials.")
        return checks

    def validate_filters(self, symbol: str, quantity: Decimal, price: Decimal) -> bool:
        if quantity <= 0:
            return False
        if price <= 0:
            return False
        if symbol.strip() == "":
            return False
        return True

    def submit_entry(self, symbol: str, side: str, quantity: Decimal, price: Decimal) -> Dict[str, Any]:
        if not self.validate_filters(symbol, quantity, price):
            return {"accepted": False, "reason": "Invalid order filters."}
        return {"accepted": True, "status": "PENDING", "client_order_id": f"{symbol}-{side.lower()}-{abs(hash(symbol+side))}"}

    def submit_protective_order(self, symbol: str, side: str, trigger_price: Decimal, quantity: Decimal) -> Dict[str, Any]:
        if not self.validate_filters(symbol, quantity, trigger_price):
            return {"accepted": False, "reason": "Invalid protective order.")
        return {"accepted": True, "status": "NEW", "client_order_id": f"{symbol}-sl-{abs(hash(symbol+side+str(trigger_price))) }"}

    def get_position(self, symbol: str) -> Dict[str, Any]:
        return {"symbol": symbol, "quantity": Decimal("0"), "side": "NONE"}

    def reconcile_orders(self) -> Dict[str, Any]:
        return {"status": "OK", "open_orders": 0}
