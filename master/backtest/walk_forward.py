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
) -> list[BacktestResult]:
    """Fit on each historical train segment and evaluate only on the following test segment."""
    results = []
    for w in windows(len(bars), train_size, test_size):
        train = bars.iloc[w.train_start:w.train_end].copy()
        test = bars.iloc[w.test_start:w.test_end].copy()
        signal_fn = signal_factory(train)
        results.append(run_backtest(test, signal_fn, config))
    return results
