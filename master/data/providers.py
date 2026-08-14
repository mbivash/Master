"""Provider abstraction for Master market data.

Yahoo is intended for historical/research data. NSE/Jugaad-style adapters can
provide polling data for paper trading. Execution must use a broker adapter.
"""
from dataclasses import dataclass
from typing import Protocol
import pandas as pd


class MarketDataProvider(Protocol):
    def history(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame: ...
    def quote(self, symbol: str) -> dict: ...


@dataclass
class YahooProvider:
    def history(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError("Install yfinance to use YahooProvider") from exc
        ticker = symbol if "." in symbol else f"{symbol}.NS"
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)
        if df.empty:
            raise ValueError(f"No Yahoo data returned for {ticker}")
        if hasattr(df.columns, "levels"):
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df = df.reset_index()
        timestamp_col = "Datetime" if "Datetime" in df.columns else "Date"
        return df.rename(columns={timestamp_col: "timestamp", "Open":"open", "High":"high", "Low":"low", "Close":"close", "Volume":"volume"})

    def quote(self, symbol: str) -> dict:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError("Install yfinance to use YahooProvider") from exc
        ticker = symbol if "." in symbol else f"{symbol}.NS"
        return dict(yf.Ticker(ticker).fast_info)


@dataclass
class JugaadProvider:
    """Optional NSE polling provider for paper trading/research."""
    def quote(self, symbol: str) -> dict:
        try:
            from jugaad_data.nse import NSELive
        except ImportError as exc:
            raise RuntimeError("Install jugaad-data to use JugaadProvider") from exc
        return NSELive().stock_quote(symbol.upper())

    def history(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        raise NotImplementedError("Use YahooProvider or a dedicated NSE historical adapter for history")
