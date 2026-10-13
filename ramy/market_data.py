from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class Candle:
    open_time: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    close_time: int
    quote_volume: Decimal = Decimal("0")
    trades: int = 0
    taker_buy_base: Decimal = Decimal("0")
    taker_buy_quote: Decimal = Decimal("0")

    @classmethod
    def from_dict(cls, payload: dict) -> "Candle":
        return cls(
            open_time=int(payload[0]),
            open=Decimal(str(payload[1])),
            high=Decimal(str(payload[2])),
            low=Decimal(str(payload[3])),
            close=Decimal(str(payload[4])),
            volume=Decimal(str(payload[5])),
            close_time=int(payload[6]),
            quote_volume=Decimal(str(payload[7])),
            trades=int(payload[8]),
            taker_buy_base=Decimal(str(payload[9])),
            taker_buy_quote=Decimal(str(payload[10])),
        )


def candle_is_valid(candle: Candle, *, allow_stale_minutes: int = 30) -> bool:
    return all([
        candle.open > 0,
        candle.high > 0,
        candle.low > 0,
        candle.close > 0,
        candle.volume >= 0,
        candle.high >= candle.low,
        candle.high >= candle.open,
        candle.high >= candle.close,
        candle.low <= candle.open,
        candle.low <= candle.close,
    ])


class MarketDataStore:
    def __init__(self) -> None:
        self._candles: dict[str, list[Candle]] = {}

    def add_candles(self, symbol: str, candles: Iterable[Candle]) -> None:
        for candle in candles:
            if not candle_is_valid(candle):
                continue
            self._candles.setdefault(symbol, []).append(candle)
        self._candles[symbol] = sorted(self._candles.get(symbol, []), key=lambda c: c.open_time)

    def get_candles(self, symbol: str) -> List[Candle]:
        return list(self._candles.get(symbol, []))

    def has_sufficient_history(self, symbol: str, min_candles: int = 200) -> bool:
        return len(self.get_candles(symbol)) >= min_candles

    def ensure_quality(self, symbol: str) -> bool:
        candles = self.get_candles(symbol)
        if len(candles) < 3:
            return False
        for previous, current in zip(candles, candles[1:]):
            if current.open_time <= previous.open_time:
                return False
        return True

    def latest_close(self, symbol: str) -> Optional[Decimal]:
        candles = self.get_candles(symbol)
        if not candles:
            return None
        return candles[-1].close
