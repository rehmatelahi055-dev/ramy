from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

from .config import BotConfig
from .indicators import compute_indicator_snapshot


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
        return Decimal(trend_score + momentum_score + volume_score + quality_score) / Decimal("100")

    def generate_signal(self, symbol: str, candles: List[dict]) -> Optional[SignalCandidate]:
        if len(candles) < self.config.min_candles_required:
            return None
        indicators = compute_indicator_snapshot(candles)
        ema9 = indicators.get("ema_9")
        ema21 = indicators.get("ema_21")
        ema50 = indicators.get("ema_50")
        rsi = indicators.get("rsi_14")
        atr = indicators.get("atr_14")
        adx = indicators.get("adx_14")
        rv = indicators.get("relative_volume")
        recent_high = indicators.get("recent_high", 0.0)
        recent_low = indicators.get("recent_low", 0.0)

        if any(v is None for v in [ema9, ema21, ema50, rsi, atr, adx, rv]):
            return None

        close = Decimal(str(candles[-1][4]))
        trend_ok = ema9 > ema21 > ema50
        momentum_ok = 45.0 <= float(rsi) <= 70.0
        volume_ok = float(rv) >= 1.0
        trend_strength = float(adx) >= 20.0
        support_zone_ok = close >= Decimal(str(recent_low)) and close <= Decimal(str(recent_high))
        if not (trend_ok and momentum_ok and volume_ok and trend_strength and support_zone_ok):
            return None

        stop = max(
            Decimal(str(recent_low)) * Decimal("0.995"),
            close - (Decimal(str(atr)) * Decimal(str(self.config.stop_loss_atr_mult))),
        )
        tp = close * (Decimal("1") + (Decimal(str(self.config.take_profit_rr)) * Decimal("0.01")))
        score = self._score_signal(40, 25, 20, 15)
        return SignalCandidate(
            symbol=symbol,
            side="BUY",
            score=score,
            reason="Spot BUY: EMA trend, RSI confirmation, strong volume, and support-zone price action.",
            entry_price=close,
            stop_loss=stop,
            take_profit=tp,
            confidence=Decimal("0.75"),
        )
