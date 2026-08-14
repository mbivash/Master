"""Optional Qlib bridge for converting validated OHLCV into research data.

Qlib is deliberately optional: Master can run its core backtester without a
local Qlib installation. When installed, this adapter exposes a clean seam
for Qlib datasets/features without coupling the trading engine to Qlib APIs.
"""

from pathlib import Path

import pandas as pd

from master.data.schema import validate_ohlcv


def to_qlib_frame(bars: pd.DataFrame, symbol: str) -> pd.DataFrame:
    df = validate_ohlcv(bars).copy()
    df["instrument"] = symbol
    df["datetime"] = df["timestamp"].dt.tz_convert(None)
    return df[["instrument", "datetime", "open", "high", "low", "close", "volume"]]


def write_qlib_csv(bars: pd.DataFrame, symbol: str, output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    to_qlib_frame(bars, symbol).to_csv(out, index=False)
    return out
