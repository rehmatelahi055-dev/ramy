from __future__ import annotations

from collections.abc import Iterable
from typing import Dict, List, Optional


def ema(values: list[float], span: int) -> Optional[float]:
    if not values or span <= 0:
        return None
    k = 2.0 / (span + 1.0)
    result = float(values[0])
    for value in values[1:]:
        result = (float(value) * k) + (result * (1.0 - k))
    return result


def rsi(values: list[float], period: int = 14) -> Optional[float]:
    if len(values) < period + 1:
        return None
    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    gains = [max(d, 0.0) for d in deltas]
    losses = [abs(min(d, 0.0)) for d in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def atr(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> Optional[float]:
    if len(closes) < period + 1:
        return None
    true_ranges: list[float] = []
    for i in range(1, min(len(closes), len(highs), len(lows))):
        prev_close = closes[i - 1]
        tr = max(highs[i] - lows[i], abs(highs[i] - prev_close), abs(lows[i] - prev_close))
        true_ranges.append(tr)
    if not true_ranges:
        return None
    return sum(true_ranges[-period:]) / period


def adx(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> Optional[float]:
    if len(closes) < period + 1:
        return None
    values: list[float] = []
    for i in range(1, len(closes)):
        up = highs[i] - highs[i - 1]
        down = lows[i - 1] - lows[i]
        if up > down and up > 0:
            values.append(up)
        elif down > up and down > 0:
            values.append(down)
        else:
            values.append(0.0)
    if not values:
        return None
    return sum(values[-period:]) / period


def relative_volume(volumes: list[float], period: int = 20) -> Optional[float]:
    if len(volumes) < period:
        return None
    recent = sum(volumes[-period:]) / period
    base = sum(volumes[:-period]) / max(1, len(volumes[:-period])) if len(volumes[:-period]) else recent
    if base == 0:
        return None
    return recent / base


def compute_indicator_snapshot(candles: list[dict]) -> Dict[str, Optional[float]]:
    closes = [float(c[4]) for c in candles]
    highs = [float(c[2]) for c in candles]
    lows = [float(c[3]) for c in candles]
    volumes = [float(c[5]) for c in candles]
    return {
        "ema_9": ema(closes, 9),
        "ema_21": ema(closes, 21),
        "ema_50": ema(closes, 50),
        "ema_200": ema(closes, 200),
        "rsi_14": rsi(closes, 14),
        "atr_14": atr(highs, lows, closes, 14),
        "adx_14": adx(highs, lows, closes, 14),
        "relative_volume": relative_volume(volumes, 20),
        "recent_high": max(closes[-20:]) if len(closes) >= 20 else max(closes),
        "recent_low": min(closes[-20:]) if len(closes) >= 20 else min(closes),
    }
