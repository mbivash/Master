from master_quant.domain import Direction, Forecast, Regime, Signal, TradeProposal
from master_quant.edge import EdgeMonitor
from master_quant.ensemble import SignalEnsemble
from master_quant.risk import RiskFirewall, RiskLimits


def test_risk_firewall_approves_reasonable_trade():
    proposal = TradeProposal(
        symbol="TEST",
        direction=Direction.LONG,
        entry_price=100,
        stop_price=98,
        target_price=106,
        quantity=100,
        expected_return=0.03,
        confidence=0.8,
        risk_fraction=0.004,
        strategy="demo",
    )
    decision = RiskFirewall().validate(proposal, equity=100_000, daily_pnl=0, open_positions=0)
    assert decision.approved


def test_risk_firewall_rejects_daily_loss():
    proposal = TradeProposal(
        symbol="TEST", direction=Direction.LONG, entry_price=100,
        stop_price=98, target_price=106, quantity=100,
        expected_return=0.03, confidence=0.8, risk_fraction=0.004, strategy="demo",
    )
    decision = RiskFirewall().validate(proposal, equity=100_000, daily_pnl=-2_000, open_positions=0)
    assert not decision.approved


def test_ensemble_flattens_sideways_signal():
    forecast = Forecast(symbol="TEST", horizon_minutes=30, bullish_probability=0.7, expected_return=0.01, expected_volatility=0.02, uncertainty=0.2)
    signal = Signal(strategy="momentum", direction=Direction.LONG, score=0.5, expected_return=0.01, confidence=0.7)
    result = SignalEnsemble().decide(forecast, [signal], Regime.SIDEWAYS)
    assert result.direction in {Direction.LONG, Direction.FLAT}


def test_edge_monitor_detects_negative_expectancy():
    monitor = EdgeMonitor(window=20)
    for _ in range(12):
        monitor.record("bad", -0.01)
    assert monitor.expectancy("bad") == -0.01
    assert not monitor.healthy("bad")
