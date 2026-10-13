# ramy

A conservative Binance USDⓈ-M Futures trading bot scaffold with configurable modes, signal generation, risk controls, paper trading support, and restart-safe persistence.

## Overview

This repository provides a modular Python implementation for:

- PAPER mode simulation
- BINANCE_FUTURES_TESTNET mode preparation
- LIVE mode disabled by default and validated
- EMA/RSI/MACD/ATR/ADX-based signal generation
- risk and position sizing engine
- SQLite persistence
- startup scripts and tests

## Default safety configuration

The project is initialized with conservative defaults that match the requested operational limits:

- starting equity: 100 USDT
- max concurrent positions: 10
- max initial margin per position: 10 USDT
- default leverage: 1x
- margin mode: ISOLATED
- risk per trade: 0.5% of current equity
- daily realized-loss limit: 2% of starting equity
- max aggregate initial margin utilization: 80%
- pause after 3 consecutive losing trades
- LIVE mode remains disabled until explicitly enabled

## Quick start

1. Create a virtual environment.
2. Install requirements.
3. Copy `.env.example` to `.env` and fill in values.
4. Start the bot in PAPER mode.

Example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m ramy --mode PAPER
```

## Windows

```powershell
powershell -ExecutionPolicy Bypass -File install_windows.ps1
python -m ramy --mode PAPER
```

## Configuration

The main configuration is in `ramy/config.py` and is loaded from environment variables. Sensitive values are never committed.

Important environment variables:

- `BOT_MODE`
- `LIVE_ENABLED`
- `BINANCE_API_KEY`
- `BINANCE_API_SECRET`
- `BINANCE_TESTNET_API_KEY`
- `BINANCE_TESTNET_API_SECRET`
- `BOT_LOG_LEVEL`

## File structure

- `ramy/` - bot modules
- `tests/` - unit tests
- `scripts/` - operational scripts
- `.env.example` - placeholders only

## Risk policy

This project uses a deliberately conservative risk model:

- risk is computed using current equity
- stop distance is included in quantity sizing
- trading is rejected when exchange rules, margin limits, or signal quality fail
- no automatic leverage escalation or martingale logic is used

## Known limitations

- Real Binance connectivity and Testnet verification require valid credentials and network access.
- This environment does not provide an execution shell; therefore, runtime testing is documented but not executed here.
- LIVE mode is intentionally blocked unless explicitly configured and confirmed.

## License

This repository is a local bot scaffold for responsible testing and paper-trading research. It is not financial advice.
