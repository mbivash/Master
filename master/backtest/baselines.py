import pandas as pd


def buy_and_hold_signal(_: pd.DataFrame) -> float:
    return 1.0


def momentum_signal(history: pd.DataFrame, lookback: int = 20) -> float:
    if len(history) <= lookback:
        return 0.0
    return 1.0 if history["close"].iloc[-1] > history["close"].iloc[-1 - lookback] else 0.0
