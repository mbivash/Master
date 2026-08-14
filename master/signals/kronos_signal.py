from dataclasses import dataclass

from master.data.schema import ForecastSummary


@dataclass(frozen=True)
class Signal:
    action: str
    expected_return: float
    confidence: float
    reason: str


def from_kronos(forecast: ForecastSummary, min_return: float = 0.0025,
                min_confidence: float = 0.55) -> Signal:
    r = forecast.expected_return
    c = forecast.confidence
    if r >= min_return and c >= min_confidence:
        action = "BUY"
    elif r <= -min_return and c >= min_confidence:
        action = "SELL"
    else:
        action = "HOLD"
    return Signal(
        action=action,
        expected_return=r,
        confidence=c,
        reason=f"Kronos expected_return={r:.4f}, confidence={c:.3f}",
    )
