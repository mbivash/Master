from datetime import datetime, timezone

from master.data.schema import ForecastSummary
from master.signals.kronos_signal import from_kronos


def forecast(ret: float, confidence: float) -> ForecastSummary:
    return ForecastSummary(
        symbol="TEST", generated_at=datetime.now(timezone.utc), horizon=12,
        last_close=100.0, expected_close=100.0 * (1 + ret),
        expected_return=ret, downside_return=ret - .01,
        upside_return=ret + .01, confidence=confidence,
    )


def test_positive_forecast_becomes_buy():
    assert from_kronos(forecast(.01, .8)).action == "BUY"


def test_weak_forecast_is_hold():
    assert from_kronos(forecast(.001, .8)).action == "HOLD"


def test_negative_forecast_becomes_sell():
    assert from_kronos(forecast(-.01, .8)).action == "SELL"


def test_low_confidence_is_hold():
    assert from_kronos(forecast(.01, .4)).action == "HOLD"
