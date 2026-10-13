from __future__ import annotations

from dataclasses import dataclass
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

    @classmethod
    def from_list(cls, payload: list) -> "Candle":
        return cls(
            open_time=int(payload[0]),
            open=Decimal(str(payload[1])),
            high=Decimal(str(payload[2])),
            low=Decimal(str(payload[3])),
            close=Decimal(str(payload[4])),
            volume=Decimal(str(payload[5])),
            close_time=int(payload[6]),
        )


class MarketDataStore:
    def __init__(self) -> None:
        self._candles: dict[str, list[Candle]] = {}

    def add_candles(self, symbol: str, candles: Iterable[Candle]) -> None:
        existing = self._candles.setdefault(symbol, [])
        for candle in candles:
            if not self._is_valid(candle):
                continue
            existing.append(candle)
        existing.sort(key=lambda c: c.open_time)

    def get_candles(self, symbol: str) -> List[Candle]:
        return list(self._candles.get(symbol, []))

    def latest_close(self, symbol: str) -> Optional[Decimal]:
        candles = self.get_candles(symbol)
        if not candles:
            return None
        return candles[-1].close

    @staticmethod
    def _is_valid(candle: Candle) -> bool:
        return bool(
            candle.open > 0
            and candle.high > 0
            and candle.low > 0
            and candle.close > 0
            and candle.high >= candle.low
            and candle.high >= candle.open
            and candle.high >= candle.close
            and candle.low <= candle.open
            and candle.low <= candle.close
        )


def candles_from_series(values: list[float], *, length: int | None = None) -> list[Candle]:
    if length is not None:
        values = values[:length]
    out: list[Candle] = []
    for i, value in enumerate(values):
        prev = values[i - 1] if i > 0 else value
        out.append(
            Candle(
                open_time=i * 300000,
                open=Decimal(str(prev)),
                high=Decimal(str(value * Decimal("1.02"))),
                low=Decimal(str(value * Decimal("0.98"))),
                close=Decimal(str(value)),
                volume=Decimal("1000"),
                close_time=(i + 1) * 300000,
            )
        )
    return out
