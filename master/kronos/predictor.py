from dataclasses import dataclass
from typing import Any

import pandas as pd

from master.data.schema import ForecastSummary, validate_ohlcv


@dataclass
class KronosConfig:
    model: str = "NeoQuasar/Kronos-small"
    tokenizer: str = "NeoQuasar/Kronos-Tokenizer-base"
    max_context: int = 512
    pred_len: int = 1
    sample_count: int = 20
    temperature: float = 0.7
    top_p: float = 0.9


class KronosPredictorAdapter:
    """Lazy Kronos adapter.

    The heavy torch/transformers stack is imported only when prediction is
    requested, keeping tests and data tooling lightweight. The adapter uses
    the official KronosPredictor interface when the Kronos package is
    installed. No network download happens during import.
    """

    def __init__(self, config: KronosConfig | None = None, predictor: Any = None):
        self.config = config or KronosConfig()
        self._predictor = predictor

    def _load(self):
        if self._predictor is None:
            try:
                from model import Kronos, KronosTokenizer, KronosPredictor
            except ImportError as exc:
                raise RuntimeError(
                    "Kronos is not installed. Clone/install the Kronos repository "
                    "or pass a predictor object for tests."
                ) from exc
            tokenizer = KronosTokenizer.from_pretrained(self.config.tokenizer)
            model = Kronos.from_pretrained(self.config.model)
            self._predictor = KronosPredictor(model, tokenizer, max_context=self.config.max_context)
        return self._predictor

    def forecast(self, symbol: str, bars: pd.DataFrame) -> ForecastSummary:
        df = validate_ohlcv(bars)
        if len(df) < 20:
            raise ValueError("Kronos requires a sufficiently long OHLCV history")
        predictor = self._load()
        x = df[["open", "high", "low", "close", "volume"]].copy()
        x.index = pd.to_datetime(df["timestamp"], utc=True).dt.tz_localize(None)
        x.index.name = "timestamps"
        x = x.tail(self.config.max_context)
        x_stamp = x.index
        y_stamp = pd.date_range(
            start=x_stamp[-1] + (x_stamp[-1] - x_stamp[-2]),
            periods=self.config.pred_len,
            freq=x_stamp[-1] - x_stamp[-2],
        )
        pred = predictor.predict(
            df=x,
            x_timestamp=x_stamp,
            y_timestamp=y_stamp,
            pred_len=self.config.pred_len,
            T=self.config.temperature,
            top_p=self.config.top_p,
            sample_count=self.config.sample_count,
        )
        close_samples = pred["close"].astype(float)
        last_close = float(x["close"].iloc[-1])
        expected_close = float(close_samples.mean())
        low = float(close_samples.min())
        high = float(close_samples.max())
        return ForecastSummary(
            symbol=symbol,
            generated_at=pd.Timestamp.utcnow().to_pydatetime(),
            horizon=self.config.pred_len,
            last_close=last_close,
            expected_close=expected_close,
            expected_return=expected_close / last_close - 1,
            downside_return=low / last_close - 1,
            upside_return=high / last_close - 1,
            confidence=max(0.0, min(1.0, 1.0 - float(close_samples.std()) / last_close)),
        )
