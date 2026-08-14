from dataclasses import dataclass
from collections import defaultdict

from master.core.contracts import SpecialistForecast


@dataclass
class SpecialistStats:
    observations: int = 0
    correct: int = 0
    cumulative_return: float = 0.0
    recent_edge: float = 0.0

    @property
    def accuracy(self) -> float:
        return self.correct / self.observations if self.observations else 0.5


class TrustEngine:
    """Evidence-based specialist weighting.

    New specialists start neutral. Weights are normalized from reliability and
    recent edge; this is deliberately simple and auditable before introducing
    learned meta-models.
    """

    def __init__(self):
        self.stats = defaultdict(SpecialistStats)

    def update(self, forecast: SpecialistForecast, realized_return: float):
        s = self.stats[forecast.specialist]
        s.observations += 1
        predicted = forecast.expected_return
        if predicted == 0 or realized_return == 0 or (predicted > 0) == (realized_return > 0):
            s.correct += 1
        s.cumulative_return += realized_return
        s.recent_edge = 0.9 * s.recent_edge + 0.1 * realized_return

    def weight(self, specialist: str) -> float:
        s = self.stats[specialist]
        return max(0.01, 0.5 * s.accuracy + 0.5 * (0.5 + s.recent_edge * 10))

    def weights(self, specialists: list[str]) -> dict[str, float]:
        raw = {name: self.weight(name) for name in specialists}
        total = sum(raw.values()) or 1.0
        return {name: value / total for name, value in raw.items()}
