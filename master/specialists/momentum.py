import pandas as pd

from master.core.contracts import Action, Specialist, SpecialistForecast


class MomentumSpecialist(Specialist):
    """Transparent baseline specialist used to challenge AI forecasts."""
    name = "momentum"

    def __init__(self, lookback: int = 20):
        self.lookback = lookback

    def predict(self, symbol: str, market: pd.DataFrame) -> SpecialistForecast:
        if len(market) < self.lookback + 1:
            raise ValueError("not enough bars for momentum specialist")
        closes = market["close"].astype(float)
        ret = float(closes.iloc[-1] / closes.iloc[-self.lookback] - 1)
        confidence = min(0.95, max(0.05, abs(ret) * 8))
        action = Action.BUY if ret > 0 else Action.SELL if ret < 0 else Action.HOLD
        return SpecialistForecast(
            specialist=self.name,
            symbol=symbol,
            action=action,
            confidence=confidence,
            expected_return=ret,
            uncertainty=1 - confidence,
            horizon=1,
            metadata={"lookback": self.lookback},
        )
