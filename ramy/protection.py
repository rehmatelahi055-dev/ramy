from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass
class CircuitBreakerState:
    name: str
    reason: str
    triggered_at: str


class CircuitBreakerManager:
    def __init__(self) -> None:
        self._events: List[CircuitBreakerState] = []

    def trigger(self, name: str, reason: str) -> None:
        self._events.append(CircuitBreakerState(name=name, reason=reason, triggered_at="NOW"))

    def active(self, name: str) -> bool:
        return any(event.name == name for event in self._events)

    def reset(self, name: str) -> None:
        self._events = [event for event in self._events if event.name != name]

    def count(self) -> int:
        return len(self._events)
