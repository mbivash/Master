import argparse
import pandas as pd

from master.backtest.engine import BacktestConfig, run_backtest
from master.backtest.kronos_strategy import make_kronos_signal
from master.kronos.predictor import KronosConfig, KronosPredictorAdapter


def main():
    parser = argparse.ArgumentParser(description="Run a paper-only Kronos historical backtest")
    parser.add_argument("csv", help="CSV containing timestamp, open, high, low, close, volume")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--pred-len", type=int, default=1)
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=0.002)
    args = parser.parse_args()

    bars = pd.read_csv(args.csv)
    adapter = KronosPredictorAdapter(KronosConfig(pred_len=args.pred_len, sample_count=args.samples))
    result = run_backtest(
        bars,
        make_kronos_signal(adapter, args.symbol, args.threshold),
        BacktestConfig(),
    )
    print(f"total_return={result.total_return:.4%}")
    print(f"max_drawdown={result.max_drawdown:.4%}")
    print(f"win_rate={result.win_rate:.4%}")
    print(f"profit_factor={result.profit_factor:.4f}")
    print(f"closed_trades={len(result.trades)}")


if __name__ == "__main__":
    main()
