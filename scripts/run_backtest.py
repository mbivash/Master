"""Run a reproducible baseline backtest.

Usage:
  python scripts/run_backtest.py path/to/ohlcv.csv

CSV columns: timestamp, open, high, low, close, volume
"""
import argparse
import pandas as pd

from master.data.schema import validate_ohlcv
from master.backtest.engine import BacktestConfig, run_backtest
from master.backtest.baselines import momentum_signal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    args = parser.parse_args()
    bars = validate_ohlcv(pd.read_csv(args.csv))
    result = run_backtest(bars, momentum_signal, BacktestConfig())
    print(f"total_return={result.total_return:.4%}")
    print(f"max_drawdown={result.max_drawdown:.4%}")
    print(f"win_rate={result.win_rate:.4%}")
    print(f"profit_factor={result.profit_factor:.3f}")
    print(f"closed_trades={len(result.trades)}")


if __name__ == "__main__":
    main()
