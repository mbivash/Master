"""Indian-market ingestion contracts.

The adapter intentionally does not hard-code a provider or scrape an exchange.
A provider supplies normalized OHLCV; Master validates and stores it. This keeps
provider credentials and licensing outside the research engine.
"""
from pathlib import Path
import pandas as pd
from master.data.schema import validate_ohlcv

SYMBOL_ALIASES = {"RELIANCE": "RELIANCE", "TCS": "TCS", "INFY": "INFY", "HDFCBANK": "HDFCBANK", "ICICIBANK": "ICICIBANK"}


def load_indian_ohlcv_csv(path: str | Path, symbol: str) -> pd.DataFrame:
    symbol = symbol.upper().strip()
    if not symbol:
        raise ValueError("symbol is required")
    df = pd.read_csv(path)
    return validate_ohlcv(df)


def split_train_test(df: pd.DataFrame, test_fraction: float = 0.2):
    if not 0 < test_fraction < 0.5:
        raise ValueError("test_fraction must be between 0 and 0.5")
    df = validate_ohlcv(df)
    cut = int(len(df) * (1 - test_fraction))
    if cut < 20 or len(df) - cut < 2:
        raise ValueError("dataset is too small for the requested split")
    return df.iloc[:cut].copy(), df.iloc[cut:].copy()
