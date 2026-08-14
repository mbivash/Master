from collections import defaultdict

from master.core.contracts import Action, MasterDecision, Specialist, SpecialistForecast
from master.core.trust import TrustEngine


class MasterBrain:
    """Meta-decision layer above independent trading specialists."""

    def __init__(self, specialists: list[Specialist], trust: TrustEngine | None = None):
        if not specialists:
            raise ValueError("Master requires at least one specialist")
        self.specialists = specialists
        self.trust = trust or TrustEngine()

    def decide(self, symbol: str, market) -> MasterDecision:
        forecasts: list[SpecialistForecast] = [s.predict(symbol, market) for s in self.specialists]
        weights = self.trust.weights([f.specialist for f in forecasts])
        action_score = defaultdict(float)
        expected = 0.0
        confidence = 0.0
        for f in forecasts:
            w = weights[f.specialist]
            direction = {Action.BUY: 1.0, Action.HOLD: 0.0, Action.SELL: -1.0}[f.action]
            action_score[f.action] += w * f.confidence
            expected += w * f.expected_return
            confidence += w * f.confidence * max(0.0, 1.0 - min(1.0, f.uncertainty))

        action = max((Action.BUY, Action.HOLD, Action.SELL), key=lambda a: action_score[a])
        rationale = "; ".join(
            f"{f.specialist}: {f.action.value} ({f.confidence:.0%}, w={weights[f.specialist]:.0%})"
            for f in forecasts
        )
        return MasterDecision(
            symbol=symbol,
            action=action,
            confidence=max(0.0, min(1.0, confidence)),
            expected_return=expected,
            specialist_weights=weights,
            votes={f.specialist: f.action for f in forecasts},
            rationale=rationale,
        )
