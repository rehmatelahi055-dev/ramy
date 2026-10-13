from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional
import os


class TradingMode(str, Enum):
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    BINANCE_FUTURES_TESTNET = "BINANCE_FUTURES_TESTNET"
    LIVE = "LIVE"


@dataclass
class BotConfig:
    mode: TradingMode = TradingMode.PAPER
    live_enabled: bool = False
    starting_equity: Decimal = Decimal("100")
    max_concurrent_positions: int = 5
    max_initial_margin_per_position: Decimal = Decimal("10")
    default_leverage: Decimal = Decimal("1")
    margin_mode: str = "ISOLATED"
    risk_per_trade_percent: Decimal = Decimal("0.5")
    daily_realized_loss_limit_percent: Decimal = Decimal("2")
    max_consecutive_losses: int = 3
    max_aggregate_initial_margin_percent: Decimal = Decimal("80")
    min_margin_buffer_ratio: Decimal = Decimal("0.10")
    stop_loss_atr_mult: Decimal = Decimal("1.5")
    take_profit_rr: Decimal = Decimal("2.0")
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    testnet_api_key: Optional[str] = None
    testnet_api_secret: Optional[str] = None
    bot_log_level: str = "INFO"
    data_source_timeout_seconds: int = 10
    exchange_base_url: str = "https://api.binance.com"
    testnet_base_url: str = "https://testnet.binance.vision"
    require_live_confirmation: bool = True
    max_symbol_scan_batch: int = 20
    min_candles_required: int = 120
    min_relative_volume: Decimal = Decimal("1.0")
    max_spread_bps: Decimal = Decimal("15")
    instrument: str = "SPOT"
    invest_per_trade: Decimal = Decimal("10")
    cap_total_investment: Decimal = Decimal("50")

    @classmethod
    def from_env(cls) -> "BotConfig":
        mode_raw = os.getenv("BOT_MODE", "PAPER")
        mode = TradingMode(mode_raw.upper())
        cfg = cls(
            mode=mode,
            live_enabled=str(os.getenv("LIVE_ENABLED", "false")).lower() == "true",
            starting_equity=Decimal(os.getenv("STARTING_EQUITY", "100")),
            max_concurrent_positions=int(os.getenv("MAX_CONCURRENT_POSITIONS", "5")),
            max_initial_margin_per_position=Decimal(os.getenv("MAX_INITIAL_MARGIN_PER_POSITION", "10")),
            default_leverage=Decimal(os.getenv("DEFAULT_LEVERAGE", "1")),
            margin_mode=os.getenv("MARGIN_MODE", "ISOLATED").upper(),
            risk_per_trade_percent=Decimal(os.getenv("RISK_PER_TRADE_PERCENT", "0.5")),
            daily_realized_loss_limit_percent=Decimal(os.getenv("DAILY_REALIZED_LOSS_LIMIT_PERCENT", "2")),
            max_consecutive_losses=int(os.getenv("MAX_CONSECUTIVE_LOSSES", "3")),
            max_aggregate_initial_margin_percent=Decimal(os.getenv("MAX_AGGREGATE_INITIAL_MARGIN_PERCENT", "80")),
            bot_log_level=os.getenv("BOT_LOG_LEVEL", "INFO").upper(),
            data_source_timeout_seconds=int(os.getenv("DATASOURCE_TIMEOUT_SECONDS", "10")),
            api_key=os.getenv("BINANCE_API_KEY") or None,
            api_secret=os.getenv("BINANCE_API_SECRET") or None,
            testnet_api_key=os.getenv("BINANCE_TESTNET_API_KEY") or None,
            testnet_api_secret=os.getenv("BINANCE_TESTNET_API_SECRET") or None,
            require_live_confirmation=str(os.getenv("LIVE_CONFIRMATION", "true")).lower() == "true",
            min_candles_required=int(os.getenv("MIN_CANDLES_REQUIRED", "120")),
            invest_per_trade=Decimal(os.getenv("INVEST_PER_TRADE", "10")),
            cap_total_investment=Decimal(os.getenv("CAP_TOTAL_INVESTMENT", "50")),
        )
        cfg.validate()
        return cfg

    def validate(self) -> None:
        if self.instrument != "SPOT":
            # We currently support SPOT only for this variant
            raise ValueError("This bot variant only supports SPOT instrument.")
        if self.starting_equity <= 0:
            raise ValueError("Starting equity must be positive.")
        if self.max_concurrent_positions <= 0 or self.max_concurrent_positions > 20:
            raise ValueError("Max concurrent positions must be between 1 and 20.")
        if self.max_initial_margin_per_position <= 0:
            raise ValueError("Max initial margin per position must be positive.")
        if self.default_leverage <= 0:
            raise ValueError("Default leverage must be positive.")
        if self.risk_per_trade_percent <= 0 or self.risk_per_trade_percent > Decimal("100"):
            raise ValueError("Risk per trade percent must be between 0 and 100.")
        if self.daily_realized_loss_limit_percent <= 0 or self.daily_realized_loss_limit_percent > Decimal("100"):
            raise ValueError("Daily realized loss limit percent must be between 0 and 100.")
        if self.max_consecutive_losses < 0:
            raise ValueError("Max consecutive losses cannot be negative.")
        if self.max_aggregate_initial_margin_percent <= 0 or self.max_aggregate_initial_margin_percent > Decimal("100"):
            raise ValueError("Aggregate initial margin percent must be between 0 and 100.")
        if self.margin_mode not in {"ISOLATED", "CROSSED"}:
            # margin_mode kept for compatibility
            pass
        if self.mode == TradingMode.LIVE and not self.live_enabled:
            raise ValueError("LIVE requires explicit LIVE_ENABLED=true.")
        if self.invest_per_trade <= 0:
            raise ValueError("INVEST_PER_TRADE must be positive.")
        if self.cap_total_investment <= 0:
            raise ValueError("CAP_TOTAL_INVESTMENT must be positive.")
        if self.invest_per_trade * self.max_concurrent_positions > self.cap_total_investment:
            raise ValueError("Invest_per_trade times max_concurrent_positions exceeds cap_total_investment. Reduce max_concurrent_positions or invest_per_trade.")
        if self.mode == TradingMode.BINANCE_FUTURES_TESTNET and self.api_key and self.testnet_api_key and self.api_key == self.testnet_api_key:
            raise ValueError("Do not mix production and testnet credentials.")
        if self.mode == TradingMode.LIVE and self.require_live_confirmation and not self.live_enabled:
            raise ValueError("LIVE mode confirmation is required and must be explicitly enabled.")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "live_enabled": self.live_enabled,
            "starting_equity": str(self.starting_equity),
            "max_concurrent_positions": self.max_concurrent_positions,
            "max_initial_margin_per_position": str(self.max_initial_margin_per_position),
            "default_leverage": str(self.default_leverage),
            "margin_mode": self.margin_mode,
            "risk_per_trade_percent": str(self.risk_per_trade_percent),
            "daily_realized_loss_limit_percent": str(self.daily_realized_loss_limit_percent),
            "max_consecutive_losses": self.max_consecutive_losses,
            "max_aggregate_initial_margin_percent": str(self.max_aggregate_initial_margin_percent),
        }


DEFAULT_CONFIG = BotConfig()


def parse_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default
