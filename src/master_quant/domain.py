from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field, field_validator


class Direction(str, Enum):
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


class Regime(str, Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    UNKNOWN = "unknown"


class Forecast(BaseModel):
    symbol: str
    horizon_minutes: int = Field(gt=0)
    bullish_probability: float = Field(ge=0, le=1)
    expected_return: float
    expected_volatility: float = Field(ge=0)
    uncertainty: float = Field(ge=0, le=1)


class Signal(BaseModel):
    strategy: str
    direction: Direction
    score: float = Field(ge=-1, le=1)
    expected_return: float
    confidence: float = Field(ge=0, le=1)
    rationale: str = ""


class TradeProposal(BaseModel):
    symbol: str
    direction: Direction
    entry_price: float = Field(gt=0)
    stop_price: float = Field(gt=0)
    target_price: float = Field(gt=0)
    quantity: int = Field(gt=0)
    expected_return: float
    confidence: float = Field(ge=0, le=1)
    risk_fraction: float = Field(ge=0, le=1)
    strategy: str

    @field_validator("stop_price", "target_price")
    @classmethod
    def positive_price(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("price must be positive")
        return value


class RiskDecision(BaseModel):
    approved: bool
    reason: str
    max_loss_fraction: float = Field(ge=0, le=1)


class TradeResult(BaseModel):
    trade_id: str
    symbol: str
    pnl: float
    return_fraction: float
    strategy: str
