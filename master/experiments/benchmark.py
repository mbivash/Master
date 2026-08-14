"""Benchmark Kronos signals against simple baselines on unseen data."""
from dataclasses import dataclass
import pandas as pd

from master.backtest.engine import BacktestConfig, run_backtest

@dataclass(frozen=True)
class BenchmarkRow:
    strategy: str
    total_return: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    trades: int


def buy_and_hold(bars: pd.DataFrame, config=BacktestConfig()):
    return run_backtest(bars, lambda _: 1.0, config)


def momentum(bars: pd.DataFrame, lookback: int = 20, config=BacktestConfig()):
    def signal(history):
        if len(history) <= lookback:
            return 0.0
        return 1.0 if float(history.close.iloc[-1]) > float(history.close.iloc[-1-lookback]) else 0.0
    return run_backtest(bars, signal, config)


def summarize(name, result) -> BenchmarkRow:
    return BenchmarkRow(name, result.total_return, result.max_drawdown, result.win_rate, result.profit_factor, len(result.trades))


def compare_baselines(bars: pd.DataFrame, config=BacktestConfig()) -> pd.DataFrame:
    results = [summarize("buy_hold", buy_and_hold(bars, config)), summarize("momentum", momentum(bars, config=config))]
    return pd.DataFrame([r.__dict__ for r in results])
