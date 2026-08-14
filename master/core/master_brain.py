from collections import defaultdict

from master.core.contracts import Action, MasterDecision, Specialist
from master.core.trust import TrustEngine
from master.core.regime_trust import RegimeTrustEngine
from master.regime.engine import classify_regime


class MasterBrain:
    """Meta-decision layer above independent specialists."""

    def __init__(self, specialists: list[Specialist], trust: TrustEngine | None = None,
                 min_confidence: float = 0.60, min_agreement: float = 0.55,
                 min_expected_return: float = 0.001):
        if not specialists:
            raise ValueError("Master requires at least one specialist")
        self.specialists = specialists
        self.trust = trust or TrustEngine()
        self.regime_trust = RegimeTrustEngine()
        self.min_confidence = min_confidence
        self.min_agreement = min_agreement
        self.min_expected_return = min_expected_return

    def decide(self, symbol: str, market) -> MasterDecision:
        forecasts = [s.predict(symbol, market) for s in self.specialists]
        regime = classify_regime(market)
        weights = self.regime_trust.weights(regime.regime, forecasts)
        action_score = defaultdict(float)
        expected = confidence = 0.0
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
            f"regime={regime.regime.value}; "
            + "; ".join(f"{f.specialist}: {f.action.value} ({f.confidence:.0%}, w={weights[f.specialist]:.0%})" for f in forecasts)
            + f"; agreement={agreement:.1%}; expected={expected:.3%}"
        )
        return MasterDecision(symbol, action, max(0.0, min(1.0, confidence)), expected, weights,
                              {f.specialist: f.action for f in forecasts}, rationale)
