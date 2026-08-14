"""Prediction outcome attribution and feedback loop for Master."""
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from master.core.contracts import Action, SpecialistForecast


@dataclass(frozen=True)
class PredictionRecord:
    created_at: datetime
    symbol: str
    forecast: SpecialistForecast
    entry_price: float
    horizon_bars: int


@dataclass(frozen=True)
class Outcome:
    specialist: str
    symbol: str
    realized_return: float
    correct: bool
    forecast_return: float


def evaluate_prediction(record: PredictionRecord, exit_price: float) -> Outcome:
    if record.entry_price <= 0 or exit_price <= 0:
        raise ValueError("prices must be positive")
    realized = exit_price / record.entry_price - 1.0
    action = record.forecast.action
    if action == Action.BUY:
        correct = realized > 0
    elif action == Action.SELL:
        correct = realized < 0
    else:
        correct = abs(realized) < 0.001
    return Outcome(
        specialist=record.forecast.specialist,
        symbol=record.symbol,
        realized_return=realized,
        correct=correct,
        forecast_return=record.forecast.expected_return,
    )


def attribution_summary(outcomes: Iterable[Outcome]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[Outcome]] = {}
    for outcome in outcomes:
        grouped.setdefault(outcome.specialist, []).append(outcome)
    result = {}
    for name, items in grouped.items():
        returns = [x.realized_return for x in items]
        result[name] = {
            "observations": float(len(items)),
            "accuracy": sum(x.correct for x in items) / len(items),
            "mean_return": sum(returns) / len(returns),
            "cumulative_return": sum(returns),
        }
    return result
