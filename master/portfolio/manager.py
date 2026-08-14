from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    average_price: float


class PortfolioManager:
    def __init__(self):
        self.positions: dict[str, Position] = {}

    def mark(self, symbol: str, price: float) -> float:
        p = self.positions.get(symbol)
        return 0.0 if p is None else p.quantity * price

    def exposure(self, prices: dict[str, float], equity: float) -> float:
        if equity <= 0:
            raise ValueError("equity must be positive")
        gross = sum(self.mark(s, p) for s, p in prices.items())
        return gross / equity
