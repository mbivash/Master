from dataclasses import dataclass
from datetime import datetime

import pandas as pd

REQUIRED_OHLCV = ("open", "high", "low", "close", "volume")


def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED_OHLCV if c not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")
    out = df.copy()
    if "timestamp" not in out.columns:
        if isinstance(out.index, pd.DatetimeIndex):
            out = out.reset_index(names="timestamp")
        else:
            raise ValueError("Data must contain a timestamp column or DatetimeIndex")
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values("timestamp").drop_duplicates("timestamp")
    if out[list(REQUIRED_OHLCV)].isna().any().any():
        raise ValueError("OHLCV contains missing values")
    if (out[["high", "low", "open", "close"]] <= 0).any().any():
        raise ValueError("Prices must be positive")
    return out.reset_index(drop=True)


@dataclass(frozen=True)
class ForecastSummary:
    symbol: str
    generated_at: datetime
    horizon: int
    last_close: float
    expected_close: float
    expected_return: float
    downside_return: float
    upside_return: float
    confidence: float
