from __future__ import annotations

from .config import BotConfig


def main() -> None:
    config = BotConfig.from_env()
    print(f"ramy initialized in {config.mode.value} mode")
    print(f"max concurrent positions: {config.max_concurrent_positions}")
    print(f"invest per trade: ${config.invest_per_trade}")
    print(f"portfolio cap: ${config.cap_total_investment}")


if __name__ == "__main__":
    main()
