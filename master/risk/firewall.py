from dataclasses import dataclass

from master.core.contracts import Action, MasterDecision


@dataclass(frozen=True)
class RiskLimits:
    max_position_fraction: float = 0.10
    max_gross_exposure: float = 1.00
    max_daily_loss: float = 0.02
    min_confidence: float = 0.60
    min_expected_return: float = 0.001


@dataclass(frozen=True)
class RiskCheck:
    approved: bool
    reason: str


class RiskFirewall:
    """Hard, deterministic gate between Master and execution."""
    def __init__(self, limits: RiskLimits | None = None):
        self.limits = limits or RiskLimits()

    def check(self, decision: MasterDecision, equity: float, current_exposure: float,
              daily_pnl: float) -> RiskCheck:
        if equity <= 0:
            return RiskCheck(False, "invalid_equity")
        if decision.action == Action.HOLD:
            return RiskCheck(True, "hold")
        if decision.confidence < self.limits.min_confidence:
            return RiskCheck(False, "confidence_below_limit")
        if abs(decision.expected_return) < self.limits.min_expected_return:
            return RiskCheck(False, "expected_return_below_limit")
        if daily_pnl / equity <= -self.limits.max_daily_loss:
            return RiskCheck(False, "daily_loss_limit")
        if current_exposure >= self.limits.max_gross_exposure:
            return RiskCheck(False, "gross_exposure_limit")
        return RiskCheck(True, "approved")
