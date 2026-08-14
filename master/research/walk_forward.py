from dataclasses import dataclass
from typing import Callable
import pandas as pd


@dataclass(frozen=True)
class WindowResult:
    train_start: object
    train_end: object
    test_start: object
    test_end: object
    test_rows: int


def rolling_windows(df: pd.DataFrame, train_bars: int, test_bars: int, step: int | None = None):
    if train_bars <= 0 or test_bars <= 0:
        raise ValueError("train_bars and test_bars must be positive")
    step = step or test_bars
    if step <= 0:
        raise ValueError("step must be positive")
    start = 0
    while start + train_bars + test_bars <= len(df):
        train = df.iloc[start:start + train_bars].copy()
        test = df.iloc[start + train_bars:start + train_bars + test_bars].copy()
        yield train, test
        start += step


def evaluate_walk_forward(df: pd.DataFrame, train_bars: int, test_bars: int,
                          evaluator: Callable[[pd.DataFrame, pd.DataFrame], dict]):
    results = []
    for train, test in rolling_windows(df, train_bars, test_bars):
        result = dict(evaluator(train, test))
        result.update({
            "train_start": train.index[0], "train_end": train.index[-1],
            "test_start": test.index[0], "test_end": test.index[-1],
            "test_rows": len(test),
        })
        results.append(result)
    return pd.DataFrame(results)
