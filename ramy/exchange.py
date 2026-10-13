from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import time
from typing import Any, Dict, Optional

try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException
except Exception:  # pragma: no cover - optional dependency
    Client = None  # type: ignore


@dataclass
class BinanceSpotAdapter:
    api_key: Optional[str]
    api_secret: Optional[str]
    testnet: bool = False
    client: Optional[Any] = None

    def connect(self) -> Dict[str, Any]:
        if Client is None:
            return {"ok": False, "reason": "python-binance not installed"}
        if not self.api_key or not self.api_secret:
            return {"ok": False, "reason": "missing api credentials"}
        try:
            self.client = Client(self.api_key, self.api_secret)
            if self.testnet:
                # python-binance older release supports set_testnet via environment or attribute
                try:
                    self.client.API_URL = "https://testnet.binance.vision/api"
                except Exception:
                    pass
            # simple ping
            _ = self.client.ping()
            server_time = self.client.get_server_time()
            return {"ok": True, "server_time": server_time}
        except Exception as exc:  # pragma: no cover - requires network
            return {"ok": False, "reason": str(exc)}

    def get_exchange_info(self) -> Dict[str, Any]:
        if not self.client:
            return {"ok": False, "reason": "not connected"}
        try:
            info = self.client.get_exchange_info()
            return {"ok": True, "info": info}
        except Exception as exc:  # pragma: no cover - requires network
            return {"ok": False, "reason": str(exc)}

    def place_test_limit_buy(self, symbol: str, price: Decimal, quantity: Decimal) -> Dict[str, Any]:
        """Place an order on Binance Spot test endpoint (uses python-binance client)."""
        if not self.client:
            return {"accepted": False, "reason": "not connected"}
        try:
            # Use test endpoint if available
            res = self.client.create_test_order(symbol=symbol, side="BUY", type="LIMIT", timeInForce="GTC", quantity=float(quantity), price=str(price))
            return {"accepted": True, "result": res}
        except Exception as exc:  # pragma: no cover - requires network
            return {"accepted": False, "reason": str(exc)}

    def close(self) -> None:
        # No persistent connection to close in python-binance
        self.client = None
