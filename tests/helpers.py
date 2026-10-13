from __future__ import annotations

from typing import Iterable


def build_trending_candles(length: int = 250) -> list[dict]:
    candles: list[dict] = []
    price = 100.0
    for i in range(length):
        price = price * 1.0025
        candles.append([
            i * 300000,
            price - 0.5,
            price + 2.5,
            price - 1.0,
            price,
            1000.0,
            (i + 1) * 300000,
            0,
            1,
            500.0,
            500.0,
        ])
    return candles


def build_bearish_candles(length: int = 250) -> list[dict]:
    candles: list[dict] = []
    price = 100.0
    for i in range(length):
        price = price * 0.9975
        candles.append([
            i * 300000,
            price + 0.5,
            price + 1.5,
            price - 2.5,
            price,
            1100.0,
            (i + 1) * 300000,
            0,
            1,
            550.0,
            550.0,
        ])
    return candles
