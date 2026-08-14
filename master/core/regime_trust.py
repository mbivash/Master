"""Regime-conditioned specialist trust."""
from collections import defaultdict

from master.core.contracts import SpecialistForecast
from master.core.trust import TrustEngine
from master.regime.engine import Regime


class RegimeTrustEngine:
    def __init__(self, floor: float = 0.05, ceiling: float = 0.60):
        self.engines = defaultdict(lambda: TrustEngine(floor=floor, ceiling=ceiling))

    def observe(self, regime: Regime, forecast: SpecialistForecast, realized_return: float) -> None:
        self.engines[regime.value].observe(forecast, realized_return)

    def weights(self, regime: Regime, forecasts: list[SpecialistForecast]) -> dict[str, float]:
        return self.engines[regime.value].weights(forecasts)

    def performance(self) -> dict[str, dict[str, dict[str, float]]]:
        result = {}
        for regime, engine in self.engines.items():
            result[regime] = {
                name: {
                    "observations": float(stats.observations),
                    "accuracy": stats.accuracy,
                    "recent_edge": stats.recent_edge,
                }
                for name, stats in engine.stats.items()
            }
        return result
