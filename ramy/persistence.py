from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


DB_PATH = "ramy_state.db"


class SQLiteStore:
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self.init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    side TEXT,
                    score TEXT,
                    reason TEXT,
                    created_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    side TEXT,
                    quantity TEXT,
                    entry_price TEXT,
                    stop_loss TEXT,
                    take_profit TEXT,
                    status TEXT,
                    created_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    order_type TEXT,
                    side TEXT,
                    quantity TEXT,
                    price TEXT,
                    client_order_id TEXT,
                    status TEXT,
                    created_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS circuit_breakers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    reason TEXT,
                    triggered_at TEXT
                )
                """
            )

    def save_signal(self, symbol: str, side: str, score: str, reason: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO signals (symbol, side, score, reason, created_at) VALUES (?, ?, ?, ?, ?)",
                (symbol, side, score, reason, datetime.utcnow().isoformat()),
            )

    def save_position(self, symbol: str, side: str, quantity: str, entry_price: str, stop_loss: str, take_profit: str, status: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO positions (symbol, side, quantity, entry_price, stop_loss, take_profit, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (symbol, side, quantity, entry_price, stop_loss, take_profit, status, datetime.utcnow().isoformat()),
            )

    def save_order(self, symbol: str, order_type: str, side: str, quantity: str, price: str, client_order_id: str, status: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO orders (symbol, order_type, side, quantity, price, client_order_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (symbol, order_type, side, quantity, price, client_order_id, status, datetime.utcnow().isoformat()),
            )

    def record_circuit_breaker(self, name: str, reason: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO circuit_breakers (name, reason, triggered_at) VALUES (?, ?, ?)",
                (name, reason, datetime.utcnow().isoformat()),
            )

    def list_orders(self) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
            return [dict(row) for row in rows]
