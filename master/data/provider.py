from typing import Protocol
import pandas as pd

class MarketDataProvider(Protocol):
    def history(self, symbol: str, start=None, end=None, interval: str = "1d") -> pd.DataFrame: ...
    def latest(self, symbols: list[str], interval: str = "1d") -> dict[str, pd.DataFrame]: ...


def normalize_provider_frame(df: pd.DataFrame) -> pd.DataFrame:
    from master.data.schema import validate_ohlcv
    return validate_ohlcv(df)
