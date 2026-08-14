from dataclasses import dataclass
import math
import pandas as pd

@dataclass(frozen=True)
class Performance:
    total_return: float
    annualized_return: float
    volatility: float
    sharpe: float
    max_drawdown: float
    profit_factor: float


def evaluate_equity(equity: pd.Series, periods_per_year: int = 252) -> Performance:
    if len(equity) < 2 or (equity <= 0).any():
        raise ValueError("equity must contain at least two positive observations")
    r = equity.astype(float).pct_change().dropna()
    total = float(equity.iloc[-1] / equity.iloc[0] - 1)
    ann = float((1 + total) ** (periods_per_year / max(len(r), 1)) - 1)
    vol = float(r.std(ddof=1) * math.sqrt(periods_per_year)) if len(r) > 1 else 0.0
    sharpe = float((r.mean() / r.std(ddof=1)) * math.sqrt(periods_per_year)) if len(r) > 1 and r.std(ddof=1) > 0 else 0.0
    dd = equity / equity.cummax() - 1
    gains = r[r > 0].sum()
    losses = -r[r < 0].sum()
    pf = float(gains / losses) if losses else float("inf") if gains else 0.0
    return Performance(total, ann, vol, sharpe, float(dd.min()), pf)
