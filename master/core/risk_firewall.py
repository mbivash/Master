from dataclasses import dataclass

from master.core.contracts import Action, MasterDecision


@dataclass(frozen=True)
class RiskLimits:
    max_position_fraction: float = 0.10
    max_daily_loss_fraction: float = 0.02
    min_confidence: float = 0.60
    min_expected_return: float = 0.001


@dataclass(frozen=True)
class RiskApproval:
    approved: bool
    reason: str
    position_fraction: float = 0.0


class RiskFirewall:
    """Hard gate that Master cannot override."""

    def __init__(self, limits: RiskLimits | None = None):
        self.limits = limits or RiskLimits()

    def approve(self, decision: MasterDecision, daily_pnl_fraction: float = 0.0) -> RiskApproval:
        if decision.action is Action.HOLD:
            return RiskApproval(False, "HOLD decision")
        if daily_pnl_fraction <= -self.limits.max_daily_loss_fraction:
            return RiskApproval(False, "daily loss limit reached")
        if decision.confidence < self.limits.min_confidence:
            return RiskApproval(False, "confidence below risk threshold")
        expected = decision.expected_return if decision.action is Action.BUY else -decision.expected_return
        if expected < self.limits.min_expected_return:
            return RiskApproval(False, "expected return below threshold")
        return RiskApproval(True, "risk checks passed", self.limits.max_position_fraction)
