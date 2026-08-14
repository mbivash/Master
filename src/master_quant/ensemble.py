from __future__ import annotations

from statistics import fmean

from .domain import Direction, Forecast, Regime, Signal


class SignalEnsemble:
    """Deterministic signal fusion; model adapters can feed signals into it."""

    def decide(self, forecast: Forecast, signals: list[Signal], regime: Regime) -> Signal:
        components = [forecast.bullish_probability * 2 - 1]
        components.extend(s.score for s in signals)
        score = max(-1.0, min(1.0, fmean(components)))

        if regime is Regime.HIGH_VOLATILITY:
            score *= 0.5
        elif regime is Regime.SIDEWAYS:
            score *= 0.7

        direction = Direction.LONG if score > 0.15 else Direction.SHORT if score < -0.15 else Direction.FLAT
        confidence = min(1.0, abs(score) * 0.75 + forecast.uncertainty * 0.0)
        expected = forecast.expected_return + fmean([s.expected_return for s in signals]) if signals else forecast.expected_return
        return Signal(
            strategy="master-ensemble",
            direction=direction,
            score=score,
            expected_return=expected,
            confidence=confidence,
            rationale=f"regime={regime.value}; components={len(components)}",
        )
