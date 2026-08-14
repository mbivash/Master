from dataclasses import dataclass
from typing import Callable

import pandas as pd

from .engine import BacktestConfig, BacktestResult, run_backtest


@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


def windows(n: int, train_size: int, test_size: int, step: int | None = None):
    if train_size <= 0 or test_size <= 0:
        raise ValueError("train_size and test_size must be positive")
    step = test_size if step is None else step
    start = 0
    while start + train_size + test_size <= n:
        yield WalkForwardWindow(start, start + train_size, start + train_size, start + train_size + test_size)
        start += step


def run_walk_forward(
    bars: pd.DataFrame,
    signal_factory: Callable[[pd.DataFrame], Callable[[pd.DataFrame], float]],
    train_size: int,
    test_size: int,
    config: BacktestConfig = BacktestConfig(),
) -> pd.DataFrame:
    """Fit on historical train segments and evaluate only on subsequent unseen data."""
    rows = []
    for w in windows(len(bars), train_size, test_size):
        train = bars.iloc[w.train_start:w.train_end].copy()
        test = bars.iloc[w.test_start:w.test_end].copy()
        signal_fn = signal_factory(train)
        result: BacktestResult = run_backtest(test, signal_fn, config)
        rows.append({
            "train_start": w.train_start,
            "train_end": w.train_end,
            "test_start": w.test_start,
            "test_end": w.test_end,
            "total_return": result.total_return,
            "max_drawdown": result.max_drawdown,
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "trades": len(result.trades),
        })
    return pd.DataFrame(rows)
