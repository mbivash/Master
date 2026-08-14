from dataclasses import dataclass
from datetime import datetime

from master.core.contracts import Action


@dataclass(frozen=True)
class PaperOrder:
    timestamp: datetime
    symbol: str
    action: Action
    quantity: float
    price: float


class PaperBroker:
    """Deterministic paper broker. Never sends orders to a real broker."""
    def __init__(self, cash: float = 100_000.0):
        if cash <= 0:
            raise ValueError("cash must be positive")
        self.cash = cash
        self.positions: dict[str, float] = {}
        self.orders: list[PaperOrder] = []

    def submit(self, symbol: str, action: Action, quantity: float, price: float, timestamp: datetime) -> PaperOrder:
        if quantity <= 0 or price <= 0:
            raise ValueError("quantity and price must be positive")
        if action == Action.BUY:
            cost = quantity * price
            if cost > self.cash:
                raise ValueError("insufficient paper cash")
            self.cash -= cost
            self.positions[symbol] = self.positions.get(symbol, 0.0) + quantity
        elif action == Action.SELL:
            held = self.positions.get(symbol, 0.0)
            if quantity > held:
                raise ValueError("insufficient paper position")
            self.positions[symbol] = held - quantity
            self.cash += quantity * price
        order = PaperOrder(timestamp, symbol, action, quantity, price)
        self.orders.append(order)
        return order
