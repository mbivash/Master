from __future__ import annotations

from dataclasses import dataclass

from .domain import Direction, RiskDecision, TradeProposal


@dataclass(frozen=True)
class RiskLimits:
    max_risk_per_trade: float = 0.005
    max_daily_loss: float = 0.015
    max_open_positions: int = 5
    min_reward_risk: float = 1.5
    max_position_value_fraction: float = 0.20


class RiskFirewall:
    """Non-agent-controlled safety boundary for trade proposals."""

    def __init__(self, limits: RiskLimits | None = None) -> None:
        self.limits = limits or RiskLimits()

    def validate(
        self,
        proposal: TradeProposal,
        *,
        equity: float,
        daily_pnl: float,
        open_positions: int,
    ) -> RiskDecision:
        if proposal.direction is Direction.FLAT:
            return RiskDecision(approved=False, reason="flat proposal", max_loss_fraction=0)
        if equity <= 0:
            return RiskDecision(approved=False, reason="invalid equity", max_loss_fraction=0)
        if daily_pnl <= -equity * self.limits.max_daily_loss:
            return RiskDecision(approved=False, reason="daily loss limit reached", max_loss_fraction=0)
        if open_positions >= self.limits.max_open_positions:
            return RiskDecision(approved=False, reason="maximum open positions reached", max_loss_fraction=0)
        if proposal.risk_fraction > self.limits.max_risk_per_trade:
            return RiskDecision(approved=False, reason="per-trade risk limit exceeded", max_loss_fraction=0)

        risk_per_share = abs(proposal.entry_price - proposal.stop_price)
        reward_per_share = abs(proposal.target_price - proposal.entry_price)
        if risk_per_share <= 0:
            return RiskDecision(approved=False, reason="invalid stop distance", max_loss_fraction=0)
        reward_risk = reward_per_share / risk_per_share
        if reward_risk < self.limits.min_reward_risk:
            return RiskDecision(approved=False, reason="reward/risk below threshold", max_loss_fraction=0)

        position_value = proposal.entry_price * proposal.quantity
        if position_value > equity * self.limits.max_position_value_fraction:
            return RiskDecision(approved=False, reason="position value limit exceeded", max_loss_fraction=0)

        return RiskDecision(
            approved=True,
            reason="risk checks passed",
            max_loss_fraction=proposal.risk_fraction,
        )
