# ramy

A conservative Binance SPOT trading bot scaffold with configurable modes, signal generation, risk controls, paper trading support, and restart-safe persistence.

This variant focuses on SPOT trading with a cap of $50 total allocation and $10 per qualified coin by default.

Quick start:

1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. cp .env.example .env
5. python -m ramy --mode PAPER

See .env.example for configuration options.
