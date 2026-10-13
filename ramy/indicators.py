from __future__ import annotations

from collections import deque
from decimal import Decimal
from statistics import mean
from typing import Dict, Iterable, List, Optional


def ema(values: Iterable[float], span: int) -> Optional[float]:
    seq = list(values)
    if not seq or span <= 0:
        return None
    k = 2 / (span + 1)
    ema_value = float(seq[0])
    for value in seq[1:]:
        ema_value = (float(value) * k) + (ema_value * (1 - k))
    return float(ema_value)


def rsi(values: Iterable[float], period: int = 14) -> Optional[float]:
    seq = list(values)
    if len(seq) < period + 1:
        return None
    deltas = [seq[i] - seq[i - 1] for i in range(1, len(seq))]
    gains = [max(delta, 0.0) for delta in deltas]
    losses = [abs(min(delta, 0.0)) for delta in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def macd(values: Iterable[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Optional[float]]:
    seq = list(values)
    if len(seq) < slow:
        return {"macd": None, "signal": None, "hist": None}
    fast_ema = ema(seq, fast)
    slow_ema = ema(seq, slow)
    if fast_ema is None or slow_ema is None:
        return {"macd": None, "signal": None, "hist": None}
    macd_value = fast_ema - slow_ema
    signal_value = None
    hist_value = None
    if len(seq) >= slow + signal:
        signal_value = ema([macd_value] if False else [0.0], signal)
    return {"macd": macd_value, "signal": signal_value, "hist": macd_value - (signal_value or 0.0)}


def atr(prices: Iterable[tuple[float, float, float]], period: int = 14) -> Optional[float]:
    rows = list(prices)
    if len(rows) < period + 1:
        return None
    true_ranges = []
    for idx in range(1, len(rows)):
        prev_high, prev_low, prev_close = rows[idx - 1]
        high, low, close = rows[idx]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)
    return sum(true_ranges[-period:]) / period if true_ranges else None


def adx(highs: Iterable[float], lows: Iterable[float], closes: Iterable[float], period: int = 14) -> Optional[float]:
    high = list(highs)
    low = list(lows)
    close = list(closes)
    if len(high) < period + 1:
        return None
    dx_values = []
    for idx in range(1, len(close)):
        up_move = high[idx] - high[idx - 1]
        down_move = low[idx - 1] - low[idx]
        if up_move > 0 and up_move > down_move:
            dx_values.append(up_move)
        elif down_move > 0 and down_move > up_move:
            dx_values.append(down_move)
        else:
            dx_values.append(0.0)
    if not dx_values:
        return None
    return sum(dx_values[-period:]) / period


def relative_volume(volume_history: Iterable[float], period: int = 20) -> Optional[float]:
    hist = list(volume_history)
    if len(hist) < period:
        return None
    recent = sum(hist[-period:]) / period
    base = sum(hist[:-period]) / max(1, len(hist[:-period])) if len(hist[:-period]) else recent
    if base == 0:
        return None
    return recent / base


def swing_highs_lows(values: Iterable[float], lookback: int = 20) -> Dict[str, float]:
    seq = list(values)
    if not seq:
        return {"recent_high": 0.0, "recent_low": 0.0}
    recent = seq[-lookback:]
    return {"recent_high": max(recent), "recent_low": min(recent)}


def support_resistance(values: Iterable[float], lookback: int = 20) -> Dict[str, float]:
    seq = list(values)
    if not seq:
        return {"support": 0.0, "resistance": 0.0}
    recent = seq[-lookback:]
    return {"support": min(recent), "resistance": max(recent)}


def compute_indicator_snapshot(candles: List[dict]) -> Dict[str, Optional[float]]:
    closes = [float(c[4]) for c in candles]
    highs = [float(c[2]) for c in candles]
    lows = [float(c[3]) for c in candles]
    volumes = [float(c[5]) for c in candles]
    lasts = []
    for c in candles:
        lasts.append((float(c[2]), float(c[3]), float(c[4])))
    return {
        "ema_9": ema(closes, 9),
        "ema_21": ema(closes, 21),
        "ema_50": ema(closes, 50),
        "ema_200": ema(closes, 200),
        "rsi_14": rsi(closes, 14),
        "atr_14": atr(lasts, 14),
        "adx_14": adx(highs, lows, closes, 14),
        "relative_volume": relative_volume(volumes, 20),
        "recent_high": swing_highs_lows(closes, 20)["recent_high"],
        "recent_low": swing_highs_lows(closes, 20)["recent_low"],
        "support": support_resistance(closes, 20)["support"],
        "resistance": support_resistance(closes, 20)["resistance"],
    }
