from __future__ import annotations


def build_trending_candles(length: int = 150) -> list[dict]:
    candles: list[dict] = []
    price = 100.0
    for i in range(length):
        price = price * 1.0025
        candles.append([
            i * 300000,
            price * 0.99,
            price * 1.02,
            price * 0.985,
            price,
            1000.0,
            (i + 1) * 300000,
        ])
    return candles


def build_bearish_candles(length: int = 150) -> list[dict]:
    candles: list[dict] = []
    price = 100.0
    for i in range(length):
        price = price * 0.9975
        candles.append([
            i * 300000,
            price * 1.01,
            price * 1.04,
            price * 0.98,
            price,
            1000.0,
            (i + 1) * 300000,
        ])
    return candles
