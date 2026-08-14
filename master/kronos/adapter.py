from dataclasses import dataclass

import pandas as pd

from master.data.schema import ForecastSummary, validate_ohlcv


@dataclass
class KronosConfig:
    model_name: str = "NeoQuasar/Kronos-small"
    tokenizer_name: str = "NeoQuasar/Kronos-Tokenizer-base"
    max_context: int = 512


class KronosAdapter:
    """Optional Kronos integration. Heavy ML dependencies stay outside the core install."""

    def __init__(self, config: KronosConfig | None = None):
        self.config = config or KronosConfig()
        self._predictor = None

    def load(self) -> None:
        try:
            from model import Kronos, KronosPredictor, KronosTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "Kronos is not installed. Install the Kronos source/dependencies "
                "and make its model package importable before enabling this adapter."
            ) from exc

        tokenizer = KronosTokenizer.from_pretrained(self.config.tokenizer_name)
        model = Kronos.from_pretrained(self.config.model_name)
        self._predictor = KronosPredictor(
            model, tokenizer, max_context=self.config.max_context
        )

    def forecast(self, symbol: str, df: pd.DataFrame, pred_len: int = 12,
                 sample_count: int = 8) -> ForecastSummary:
        if self._predictor is None:
            raise RuntimeError("Call load() before forecast().")
        data = validate_ohlcv(df)
        if len(data) < 32:
            raise ValueError("Not enough candles for a meaningful forecast")

        x_df = data[["open", "high", "low", "close", "volume"]].tail(
            self.config.max_context
        )
        x_timestamp = data["timestamp"].tail(len(x_df))
        freq = x_timestamp.diff().dropna().median()
        if pd.isna(freq) or freq <= pd.Timedelta(0):
            raise ValueError("Unable to infer candle frequency")
        y_timestamp = pd.date_range(
            x_timestamp.iloc[-1] + freq, periods=pred_len, freq=freq
        )

        pred = self._predictor.predict(
            df=x_df,
            x_timestamp=x_timestamp,
            y_timestamp=pd.Series(y_timestamp),
            pred_len=pred_len,
            T=1.0,
            top_p=0.9,
            sample_count=sample_count,
        )
        last_close = float(x_df["close"].iloc[-1])
        expected_close = float(pred["close"].iloc[-1])
        returns = pred["close"].astype(float) / last_close - 1.0
        return ForecastSummary(
            symbol=symbol,
            generated_at=pd.Timestamp.now(tz="UTC").to_pydatetime(),
            horizon=pred_len,
            last_close=last_close,
            expected_close=expected_close,
            expected_return=float(returns.iloc[-1]),
            downside_return=float(returns.min()),
            upside_return=float(returns.max()),
            confidence=float(1.0 / (1.0 + returns.std(ddof=0))),
        )
