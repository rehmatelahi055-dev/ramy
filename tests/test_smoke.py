from decimal import Decimal

from ramy.config import BotConfig, TradingMode
from ramy.risk import RiskEngine
from ramy.strategy import StrategyEngine
from tests.helpers import build_trending_candles, build_bearish_candles


def test_spot_buy_signal_generation():
    cfg = BotConfig(mode=TradingMode.PAPER)
    engine = StrategyEngine(cfg)
    signal = engine.generate_signal("BTCUSDT", build_trending_candles())
    assert signal is not None
    assert signal.side == "BUY"


def test_risk_budget_and_cap_limits():
    cfg = BotConfig(mode=TradingMode.PAPER)
    engine = RiskEngine(cfg)
    outcome = engine.calculate_trade_risk(
        equity=Decimal("100"),
        current_positions=[],
        entry_price=Decimal("100"),
        stop_loss=Decimal("99"),
        side="BUY",
    )
    assert outcome.passes
    assert outcome.allowed_risk_usdt == Decimal("0.5")


def test_security_requires_explicit_live_enablement():
    cfg = BotConfig(mode=TradingMode.LIVE, live_enabled=False)
    try:
        cfg.validate()
        assert False
    except ValueError:
        assert True
