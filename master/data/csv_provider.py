from pathlib import Path

import pandas as pd

from .schema import validate_ohlcv


class CSVMarketData:
    """Deterministic historical-data adapter used by research/backtests."""

    def load(self, path: str | Path) -> pd.DataFrame:
        df = pd.read_csv(path)
        return validate_ohlcv(df)
