from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional

from .indicators import compute_indicator_snapshot


def is_bullish_engulfing(candles: List[dict]) -> bool:
    if len(candles) < 2:
        return False
    prev = candles[-2]
    cur = candles[-1]
    prev_open = float(prev[1])
    prev_close = float(prev[4])
    cur_open = float(cur[1])
    cur_close = float(cur[4])
    return prev_close < prev_open and cur_close > cur_open and cur_close > prev_open and cur_open < prev_close


def is_hammer(candles: List[dict], body_ratio: float = 0.35) -> bool:
    if not candles:
        return False
    c = candles[-1]
    o = float(c[1])
    h = float(c[2])
    l = float(c[3])
    cl = float(c[4])
    body = abs(cl - o)
    range_ = h - l if h - l > 0 else 1e-9
    lower_wick = min(o, cl) - l
    return lower_wick / range_ > 0.5 and body / range_ < body_ratio and cl > o


def multi_timeframe_indicators(symbol: str, candles: List[dict]) -> Dict[str, Optional[float]]:
    # For this scaffold, we simulate multi-timeframe by taking subsamples
    indicators = compute_indicator_snapshot(candles)
    # short-term = last 20
    short_candles = candles[-50:]
    long_candles = candles[-200:]
    s_ind = compute_indicator_snapshot(short_candles) if len(short_candles) >= 20 else {}
    l_ind = compute_indicator_snapshot(long_candles) if len(long_candles) >= 50 else {}
    out = {**indicators}
    out.update({f"s_{k}": v for k, v in s_ind.items()})
    out.update({f"l_{k}": v for k, v in l_ind.items()})
    return out


def score_candidate(symbol: str, candles: List[dict]) -> float:
    ind = multi_timeframe_indicators(symbol, candles)
    score = 0.0
    # trend: ema alignment short and long
    try:
        if ind.get("ema_9") and ind.get("ema_21") and ind.get("ema_50"):
            if ind["ema_9"] > ind["ema_21"] > ind["ema_50"]:
                score += 30
    except Exception:
        pass
    # volume
    rv = ind.get("relative_volume") or 0.0
    if rv >= 1.2:
        score += 20
    # pattern
    if is_bullish_engulfing(candles):
        score += 25
    if is_hammer(candles):
        score += 15
    # momentum
    rsi = ind.get("rsi_14") or 0.0
    if 40.0 <= rsi <= 65.0:
        score += 10
    return score
