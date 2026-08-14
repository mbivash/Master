"""Download a reproducible Yahoo Finance research dataset.

Usage:
  python scripts/download_yahoo_dataset.py --symbols RELIANCE TCS INFY --period 5y --output data/raw
"""
import argparse
from pathlib import Path

from master.data.providers import YahooProvider


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--symbols", nargs="+", required=True)
    p.add_argument("--period", default="5y")
    p.add_argument("--interval", default="1d")
    p.add_argument("--output", default="data/raw")
    args = p.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    provider = YahooProvider()
    for symbol in args.symbols:
        df = provider.history(symbol, args.period, args.interval)
        target = out / f"{symbol.upper()}.csv"
        df.to_csv(target, index=False)
        print(f"saved {target} ({len(df)} rows)")


if __name__ == "__main__":
    main()
