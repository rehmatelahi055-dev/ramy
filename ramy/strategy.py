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
        return total / Decimal("100")

    def _generate_long(self, symbol: str, candles: List[dict], indicators: Dict[str, Optional[float]]) -> Optional[SignalCandidate]:
        if not candles:
            return None
        close = Decimal(str(candles[-1][4]))
        ema9 = indicators.get("ema_9")
        ema21 = indicators.get("ema_21")
        ema50 = indicators.get("ema_50")
        ema200 = indicators.get("ema_200")
        rsi = indicators.get("rsi_14")
        atr = indicators.get("atr_14")
        adx = indicators.get("adx_14")
        rv = indicators.get("relative_volume")
        recent_high = indicators.get("recent_high", 0)
        recent_low = indicators.get("recent_low", 0)
        if None in {ema9, ema21, ema50, ema200, rsi, atr, adx, rv}:
            return None

        trend_ok = ema9 > ema21 > ema50 > ema200
        momentum_ok = rsi is not None and 45.0 <= rsi <= 70.0
        volume_ok = rv >= float(self.config.min_relative_volume)
        trend_strength = adx >= 25.0
        price_above_support = close >= Decimal(str(recent_low))
        price_below_resistance = close <= Decimal(str(recent_high))

        if not (trend_ok and momentum_ok and volume_ok and trend_strength and price_above_support and price_below_resistance):
            return None

        score = self._score_signal(35, 25, 20, 20)
        reason = "Long setup: EMA alignment, RSI within range, volume expansion, and trend strength confirmed."
        stop = max(Decimal(str(recent_low)) * Decimal("0.999"), close * Decimal("0.995"))
        tp = close * (Decimal("1") + self.config.take_profit_rr * Decimal("0.01"))
        return SignalCandidate(
            symbol=symbol,
            side="LONG",
            score=score,
            reason=reason,
            entry_price=close,
            stop_loss=stop,
            take_profit=tp,
            confidence=Decimal("0.75"),
        )

    def _generate_short(self, symbol: str, candles: List[dict], indicators: Dict[str, Optional[float]]) -> Optional[SignalCandidate]:
        if not candles:
            return None
        close = Decimal(str(candles[-1][4]))
        ema9 = indicators.get("ema_9")
        ema21 = indicators.get("ema_21")
        ema50 = indicators.get("ema_50")
        ema200 = indicators.get("ema_200")
        rsi = indicators.get("rsi_14")
        atr = indicators.get("atr_14")
        adx = indicators.get("adx_14")
        rv = indicators.get("relative_volume")
        recent_high = indicators.get("recent_high", 0)
        recent_low = indicators.get("recent_low", 0)
        if None in {ema9, ema21, ema50, ema200, rsi, atr, adx, rv}:
            return None

        trend_ok = ema9 < ema21 < ema50 < ema200
        momentum_ok = rsi is not None and 30.0 <= rsi <= 55.0
        volume_ok = rv >= float(self.config.min_relative_volume)
        trend_strength = adx >= 25.0
        price_below_resistance = close <= Decimal(str(recent_high))
        price_above_support = close >= Decimal(str(recent_low))

        if not (trend_ok and momentum_ok and volume_ok and trend_strength and price_below_resistance and price_above_support):
            return None

        score = self._score_signal(35, 25, 20, 20)
        reason = "Short setup: bearish EMA alignment, RSI weakness, and volume expansion confirmed."
        stop = min(Decimal(str(recent_high)) * Decimal("1.001"), close * Decimal("1.005"))
        tp = close * (Decimal("1") - self.config.take_profit_rr * Decimal("0.01"))
        return SignalCandidate(
            symbol=symbol,
            side="SHORT",
            score=score,
            reason=reason,
            entry_price=close,
            stop_loss=stop,
            take_profit=tp,
            confidence=Decimal("0.75"),
        )

    def generate_signal(self, symbol: str, candles: List[dict]) -> Optional[SignalCandidate]:
        if len(candles) < self.config.min_candles_required:
            return None
        indicators = compute_indicator_snapshot(candles)
        long_signal = self._generate_long(symbol, candles, indicators)
        if long_signal:
            return long_signal
        return self._generate_short(symbol, candles, indicators)
