"""Deterministic, explainable market-regime classifier.

The classifier uses only information available through the current bar. It is
intended as a conditioning signal for specialist trust, not as a standalone
trading strategy.
"""
from dataclasses import dataclass
from enum import Enum

import pandas as pd


class Regime(str, Enum):
    BULL_TREND = "BULL_TREND"
    BEAR_TREND = "BEAR_TREND"
    SIDEWAYS = "SIDEWAYS"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RegimeSnapshot:
    regime: Regime
    trend_strength: float
    volatility: float
    reason: str


def classify_regime(bars: pd.DataFrame, fast: int = 20, slow: int = 50) -> RegimeSnapshot:
    if "close" not in bars or len(bars) < slow + 2:
        return RegimeSnapshot(Regime.UNKNOWN, 0.0, 0.0, "insufficient_history")
    close = pd.to_numeric(bars["close"], errors="raise")
    fast_ma = close.rolling(fast).mean().iloc[-1]
    slow_ma = close.rolling(slow).mean().iloc[-1]
    returns = close.pct_change().dropna()
    vol = float(returns.rolling(20).std().iloc[-1])
    trend = float(abs(fast_ma / slow_ma - 1.0))
    # Volatility threshold is intentionally conservative and configurable later.
    if vol >= 0.03:
        regime = Regime.HIGH_VOLATILITY
    elif fast_ma > slow_ma and trend >= 0.01:
        regime = Regime.BULL_TREND
    elif fast_ma < slow_ma and trend >= 0.01:
        regime = Regime.BEAR_TREND
    else:
        regime = Regime.SIDEWAYS
    return RegimeSnapshot(regime, trend, vol, f"fast_ma={fast_ma:.4f};slow_ma={slow_ma:.4f};vol={vol:.4f}")
