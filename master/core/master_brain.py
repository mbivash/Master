from collections import defaultdict

from master.core.contracts import Action, MasterDecision, Specialist, SpecialistForecast
from master.core.trust import TrustEngine


class MasterBrain:
    """Meta-decision layer above independent specialists.

    It can choose HOLD when model disagreement or expected return is too weak;
    it never places orders. Execution remains behind the risk firewall.
    """

    def __init__(self, specialists: list[Specialist], trust: TrustEngine | None = None,
                 min_confidence: float = 0.60, min_agreement: float = 0.55,
                 min_expected_return: float = 0.001):
        if not specialists:
            raise ValueError("Master requires at least one specialist")
        self.specialists = specialists
        self.trust = trust or TrustEngine()
        self.min_confidence = min_confidence
        self.min_agreement = min_agreement
        self.min_expected_return = min_expected_return

    def decide(self, symbol: str, market) -> MasterDecision:
        forecasts: list[SpecialistForecast] = [s.predict(symbol, market) for s in self.specialists]
        weights = self.trust.weights([f.specialist for f in forecasts])
        action_score = defaultdict(float)
        expected = 0.0
        confidence = 0.0
        for f in forecasts:
            w = weights[f.specialist]
            action_score[f.action] += w * f.confidence
            expected += w * f.expected_return
            confidence += w * f.confidence * (1.0 - min(1.0, f.uncertainty))

        action = max((Action.BUY, Action.HOLD, Action.SELL), key=lambda a: action_score[a])
        agreement = action_score[action] / max(sum(action_score.values()), 1e-12)
        if confidence < self.min_confidence or agreement < self.min_agreement:
            action = Action.HOLD
        if action != Action.HOLD and abs(expected) < self.min_expected_return:
            action = Action.HOLD

        rationale = (
            "; ".join(f"{f.specialist}: {f.action.value} ({f.confidence:.0%}, w={weights[f.specialist]:.0%})" for f in forecasts)
            + f"; agreement={agreement:.1%}; expected={expected:.3%}"
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
