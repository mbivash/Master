from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from .domain import Direction, TradeProposal, TradeResult


@dataclass
class PaperBroker:
    equity: float = 100_000.0
    daily_pnl: float = 0.0
    open_positions: int = 0

    def submit(self, proposal: TradeProposal) -> str:
        if proposal.direction is Direction.FLAT:
            raise ValueError("cannot submit a flat order")
        self.open_positions += 1
        return str(uuid4())

    def settle(self, trade_id: str, proposal: TradeProposal, exit_price: float) -> TradeResult:
        direction = 1 if proposal.direction is Direction.LONG else -1
        pnl = (exit_price - proposal.entry_price) * proposal.quantity * direction
        invested = proposal.entry_price * proposal.quantity
        return_fraction = pnl / invested if invested else 0.0
