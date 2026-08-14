"""Kronos as a Master specialist.

The specialist converts the real Kronos forecast into the common Master
contract. It does not place orders and therefore cannot bypass risk controls.
"""
from master.core.contracts import Action, Specialist, SpecialistForecast
from master.kronos.predictor import KronosPredictorAdapter, KronosConfig


class KronosSpecialist(Specialist):
    name = "kronos"

    def __init__(self, predictor: KronosPredictorAdapter | None = None):
        self.predictor = predictor or KronosPredictorAdapter(KronosConfig(pred_len=1, sample_count=20))

    def predict(self, symbol: str, market):
        forecast = self.predictor.forecast(symbol, market)
        if forecast.expected_return > 0:
            action = Action.BUY
        elif forecast.expected_return < 0:
            action = Action.SELL
        else:
            action = Action.HOLD
        return SpecialistForecast(
            specialist=self.name,
            symbol=symbol,
            action=action,
            confidence=forecast.confidence,
            expected_return=forecast.expected_return,
            uncertainty=max(0.0, forecast.upside_return - forecast.downside_return) / 2,
            horizon=forecast.horizon,
            metadata={
                "last_close": forecast.last_close,
                "upside_return": forecast.upside_return,
                "downside_return": forecast.downside_return,
            },
        )
