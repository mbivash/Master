from master.kronos.predictor import KronosPredictorAdapter


def make_kronos_signal(adapter: KronosPredictorAdapter, symbol: str, threshold: float = 0.002):
    """Return a backtester-compatible signal callback.

    The callback only sees bars up to the current timestamp. The backtester
    executes on the next bar, avoiding look-ahead bias.
    """
    def signal(history):
        forecast = adapter.forecast(symbol, history)
        if forecast.confidence < 0.55:
            return 0.0
        if forecast.expected_return >= threshold:
            return min(1.0, forecast.expected_return / threshold)
        return 0.0

    return signal
