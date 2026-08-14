from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class Window:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


def expanding_windows(n: int, train_size: int, test_size: int, step: int | None = None):
    if train_size < 20 or test_size < 1:
        raise ValueError("invalid window sizes")
    step = step or test_size
    start = 0
    while start + train_size + test_size <= n:
        yield Window(start, start + train_size, start + train_size, start + train_size + test_size)
        start += step


def evaluate_windows(bars: pd.DataFrame, runner, train_size: int, test_size: int):
    results = []
    for w in expanding_windows(len(bars), train_size, test_size):
        train = bars.iloc[w.train_start:w.train_end].copy()
        test = bars.iloc[w.test_start:w.test_end].copy()
        result = runner(train, test)
        results.append({"window": w, "result": result})
    return results
