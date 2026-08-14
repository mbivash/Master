from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Action(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class SpecialistForecast:
    specialist: str
    symbol: str
    action: Action
    confidence: float
    expected_return: float
    uncertainty: float = 0.0
    horizon: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.uncertainty < 0:
            raise ValueError("uncertainty cannot be negative")


@dataclass(frozen=True)
class MasterDecision:
    symbol: str
    action: Action
    confidence: float
    expected_return: float
    specialist_weights: dict[str, float]
    votes: dict[str, Action]
    rationale: str


class Specialist:
    name: str

    def predict(self, symbol: str, market: Any) -> SpecialistForecast:
        raise NotImplementedError
