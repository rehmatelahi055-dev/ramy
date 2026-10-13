from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Iterable, List, Optional

from .config import BotConfig
from .indicators import compute_indicator_snapshot
from .market_data import Candle


@dataclass
class SignalCandidate:
    symbol: str
    side: str
    score: Decimal
    reason: str
    entry_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    confidence: Decimal = Decimal("0")


class StrategyEngine:
    def __init__(self, config: BotConfig) -> None:
        self.config = config

    def _score_signal(self, trend_score: int, momentum_score: int, volume_score: int, quality_score: int) -> Decimal:
        total = Decimal(trend_score + momentum_score + volume_score + quality_score)
        # scale to 0-1
        return total / Decimal("100")

    def _generate_buy(self, symbol: str, candles: List[dict], indicators: Dict[str, Optional[float]]) -> Optional[SignalCandidate]:
        if not candles:
            return None
        close = Decimal(str(candles[-1][4]))
        ema9 = indicators.get("ema_9")
        ema21 = indicators.get("ema_21")
        ema50 = indicators.get("ema_50")
        rsi = indicators.get("rsi_14")
        atr = indicators.get("atr_14")
        adx = indicators.get("adx_14")
        rv = indicators.get("relative_volume")
        recent_high = indicators.get("recent_high", 0)
        recent_low = indicators.get("recent_low", 0)
        if None in {ema9, ema21, ema50, rsi, atr, adx, rv}:
            return None

        # Basic bullish checks for spot buy
        trend_ok = ema9 > ema21 > ema50
        momentum_ok = rsi is not None and 40.0 <= rsi <= 70.0
        volume_ok = rv is not None and rv >= float(self.config.min_relative_volume)
        trend_strength = adx >= 20.0
        price_near_support = close <= Decimal(str(recent_high)) and close >= Decimal(str(recent_low))

        if not (trend_ok and momentum_ok and volume_ok and trend_strength and price_near_support):
            return None

        score = self._score_signal(40, 25, 20, 15)
        reason = "Spot buy: EMA alignment, RSI range, volume, and ADX trend strength"
        stop = max(Decimal(str(recent_low)) * Decimal("0.995"), close - Decimal(str(atr or 0)) * Decimal("1.5"))
        tp = close * (Decimal("1") + Decimal(str(self.config.take_profit_rr)) * Decimal("0.01"))
        return SignalCandidate(
            symbol=symbol,
            side="BUY",
            score=score,
            reason=reason,
            entry_price=close,
            stop_loss=stop,
            take_profit=tp,
            confidence=Decimal("0.7"),
        )

    def generate_signal(self, symbol: str, candles: List[dict]) -> Optional[SignalCandidate]:
        if len(candles) < self.config.min_candles_required:
            return None
        indicators = compute_indicator_snapshot(candles)
        buy = self._generate_buy(symbol, candles, indicators)
        return buy
