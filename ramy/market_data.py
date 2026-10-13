from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Dict, Optional


class TradingMode(str, Enum):
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    BINANCE_TESTNET = "BINANCE_TESTNET"
    LIVE = "LIVE"


@dataclass
class BotConfig:
    mode: TradingMode = TradingMode.PAPER
    live_enabled: bool = False
    starting_equity: Decimal = Decimal("100")
    max_concurrent_positions: int = 5
    invest_per_trade: Decimal = Decimal("10")
    cap_total_investment: Decimal = Decimal("50")
    risk_per_trade_percent: Decimal = Decimal("0.5")
    daily_loss_limit_percent: Decimal = Decimal("2")
    max_consecutive_losses: int = 3
    default_leverage: Decimal = Decimal("1")
    margin_mode: str = "ISOLATED"
    min_candles_required: int = 120
    take_profit_rr: Decimal = Decimal("2.0")
    stop_loss_atr_mult: Decimal = Decimal("1.5")
    max_symbol_scan_batch: int = 20
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    testnet_api_key: Optional[str] = None
    testnet_api_secret: Optional[str] = None
    bot_log_level: str = "INFO"
    data_source_timeout_seconds: int = 10
    exchange_base_url: str = "https://api.binance.com"
    testnet_base_url: str = "https://testnet.binance.vision"
    require_live_confirmation: bool = True
    instrument: str = "SPOT"

    @classmethod
    def from_env(cls) -> "BotConfig":
        mode = TradingMode(os.getenv("BOT_MODE", "PAPER").upper())
        cfg = cls(
            mode=mode,
            live_enabled=str(os.getenv("LIVE_ENABLED", "false")).lower() == "true",
            starting_equity=_d(os.getenv("STARTING_EQUITY", "100")),
            max_concurrent_positions=int(os.getenv("MAX_CONCURRENT_POSITIONS", "5")),
            invest_per_trade=_d(os.getenv("INVEST_PER_TRADE", "10")),
            cap_total_investment=_d(os.getenv("CAP_TOTAL_INVESTMENT", "50")),
            risk_per_trade_percent=_d(os.getenv("RISK_PER_TRADE_PERCENT", "0.5")),
            daily_loss_limit_percent=_d(os.getenv("DAILY_REALIZED_LOSS_LIMIT_PERCENT", "2")),
            max_consecutive_losses=int(os.getenv("MAX_CONSECUTIVE_LOSSES", "3")),
            default_leverage=_d(os.getenv("DEFAULT_LEVERAGE", "1")),
            margin_mode=os.getenv("MARGIN_MODE", "ISOLATED").upper(),
            min_candles_required=int(os.getenv("MIN_CANDLES_REQUIRED", "120")),
            take_profit_rr=_d(os.getenv("TAKE_PROFIT_RR", "2.0")),
            stop_loss_atr_mult=_d(os.getenv("STOP_LOSS_ATR_MULT", "1.5")),
            api_key=os.getenv("BINANCE_API_KEY") or None,
            api_secret=os.getenv("BINANCE_API_SECRET") or None,
            testnet_api_key=os.getenv("BINANCE_TESTNET_API_KEY") or None,
            testnet_api_secret=os.getenv("BINANCE_TESTNET_API_SECRET") or None,
            bot_log_level=os.getenv("BOT_LOG_LEVEL", "INFO").upper(),
            data_source_timeout_seconds=int(os.getenv("DATASOURCE_TIMEOUT_SECONDS", "10")),
            require_live_confirmation=str(os.getenv("LIVE_CONFIRMATION", "true")).lower() == "true",
        )
        cfg.validate()
        return cfg

    def validate(self) -> None:
        if self.instrument != "SPOT":
            raise ValueError("This bot is for SPOT trading only.")
        if self.starting_equity <= 0:
            raise ValueError("Starting equity must be positive.")
        if self.max_concurrent_positions <= 0 or self.max_concurrent_positions > 20:
            raise ValueError("Max concurrent positions must be between 1 and 20.")
        if self.invest_per_trade <= 0:
            raise ValueError("INVEST_PER_TRADE must be positive.")
        if self.cap_total_investment <= 0:
            raise ValueError("CAP_TOTAL_INVESTMENT must be positive.")
        if self.invest_per_trade * Decimal(self.max_concurrent_positions) > self.cap_total_investment:
            raise ValueError("Invest per trade times max positions exceeds the total cash cap.")
        if self.risk_per_trade_percent <= 0 or self.risk_per_trade_percent > Decimal("10"):
            raise ValueError("Risk per trade must be between 0 and 10%.")
        if self.daily_loss_limit_percent <= 0 or self.daily_loss_limit_percent > Decimal("100"):
            raise ValueError("Daily loss limit percent must be between 0 and 100.")
        if self.max_consecutive_losses < 0:
            raise ValueError("Max consecutive losses cannot be negative.")
        if self.default_leverage <= 0:
            raise ValueError("Default leverage must be positive.")
        if self.mode == TradingMode.LIVE and not self.live_enabled:
            raise ValueError("LIVE mode requires LIVE_ENABLED=true.")
        if self.mode == TradingMode.LIVE and self.require_live_confirmation and not self.live_enabled:
            raise ValueError("LIVE mode confirmation is required.")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "live_enabled": self.live_enabled,
            "starting_equity": str(self.starting_equity),
            "max_concurrent_positions": self.max_concurrent_positions,
            "invest_per_trade": str(self.invest_per_trade),
            "cap_total_investment": str(self.cap_total_investment),
            "risk_per_trade_percent": str(self.risk_per_trade_percent),
            "daily_loss_limit_percent": str(self.daily_loss_limit_percent),
            "max_consecutive_losses": self.max_consecutive_losses,
        }


def _d(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default


DEFAULT_CONFIG = BotConfig()
