"""Qlib-backed specialist seam.

Qlib is optional. The specialist accepts a fitted predictor implementing
predict(features) -> numeric return, keeping model training separate from
Master's orchestration and avoiding fake predictions when Qlib is absent.
"""
from typing import Any
import pandas as pd
from master.core.contracts import Action, Specialist, SpecialistForecast


class QlibSpecialist(Specialist):
    name = "qlib"

    def __init__(self, predictor: Any = None, feature_fn=None):
        self.predictor = predictor
        self.feature_fn = feature_fn or self._default_features

    @staticmethod
    def _default_features(market: pd.DataFrame) -> pd.DataFrame:
        x = market.copy()
        x["ret_1"] = x["close"].pct_change()
        x["ret_5"] = x["close"].pct_change(5)
        x["vol_20"] = x["close"].pct_change().rolling(20).std()
        x["ma_ratio"] = x["close"].rolling(20).mean() / x["close"].rolling(50).mean() - 1
        return x.dropna()

    def predict(self, symbol: str, market: pd.DataFrame) -> SpecialistForecast:
        if self.predictor is None:
            raise RuntimeError("Qlib specialist requires a fitted predictor")
        features = self.feature_fn(market)
        if features.empty:
            raise ValueError("not enough market history for Qlib features")
        predicted = float(self.predictor.predict(features).iloc[-1] if hasattr(self.predictor.predict(features), "iloc") else self.predictor.predict(features))
        confidence = max(0.05, min(0.95, abs(predicted) * 10))
        action = Action.BUY if predicted > 0 else Action.SELL if predicted < 0 else Action.HOLD
        return SpecialistForecast(self.name, symbol, action, confidence, predicted, 1-confidence, 1, {"feature_count": len(features.columns)})
