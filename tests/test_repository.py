from decimal import Decimal

from ramy.config import BotConfig, TradingMode
from ramy.risk import RiskEngine
from ramy.strategy import StrategyEngine
from tests.helpers import build_trending_candles


def test_buy_signal_generation():
    cfg = BotConfig(mode=TradingMode.PAPER)
    signal = StrategyEngine(cfg).generate_signal("BTCUSDT", build_trending_candles())
    assert signal is not None
    assert signal.side == "BUY"


def test_risk_budget_and_cap_limits():
    cfg = BotConfig(mode=TradingMode.PAPER)
    result = RiskEngine(cfg).calculate_trade_risk(
        equity=Decimal("100"),
        current_positions=[],
        entry_price=Decimal("100"),
        stop_loss=Decimal("99"),
        side="BUY",
    )
    assert result.passes is True
    assert result.notional == Decimal("10")


def test_live_requires_explicit_enablement():
    cfg = BotConfig(mode=TradingMode.LIVE, live_enabled=False)
    try:
        cfg.validate()
        raise AssertionError("LIVE mode should fail without explicit enablement")
    except ValueError:
        pass
