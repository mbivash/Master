from dataclasses import dataclass, field
from math import exp

from master.core.contracts import Action, SpecialistForecast


@dataclass
class SpecialistStats:
    observations: int = 0
    correct: int = 0
    pnl_samples: list[float] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.correct / self.observations if self.observations else 0.5

    @property
    def recent_edge(self) -> float:
        if not self.pnl_samples:
            return 0.0
        window = self.pnl_samples[-50:]
        return sum(window) / len(window)


class TrustEngine:
    """Auditable, evidence-based specialist weighting.

    Specialists start neutral. Only realized outcomes can change trust. A
    floor and ceiling prevent an untested or recently lucky model from taking
    over the ensemble.
    """

    def __init__(self, floor: float = 0.05, ceiling: float = 0.60):
        self.floor = floor
        self.ceiling = ceiling
        self.stats: dict[str, SpecialistStats] = {}

    def observe(self, forecast: SpecialistForecast, realized_return: float) -> None:
        s = self.stats.setdefault(forecast.specialist, SpecialistStats())
        s.observations += 1
        correct = (
            (forecast.action == Action.BUY and realized_return > 0)
            or (forecast.action == Action.SELL and realized_return < 0)
            or (forecast.action == Action.HOLD and abs(realized_return) < 0.001)
        )
        if correct:
            s.correct += 1
        s.pnl_samples.append(float(realized_return))

    # Backwards-compatible name for existing callers.
    update = observe

    def _raw_weight(self, specialist: str) -> float:
        s = self.stats.get(specialist, SpecialistStats())
        accuracy_score = s.accuracy
        # Squash recent edge to [0, 1], avoiding huge weight swings.
        edge_score = 1.0 / (1.0 + exp(-20.0 * s.recent_edge))
        return max(self.floor, 0.5 * accuracy_score + 0.5 * edge_score)

    def weights(self, specialists: list[str]) -> dict[str, float]:
        if not specialists:
            return {}
        raw = {name: self._raw_weight(name) for name in specialists}
        total = sum(raw.values()) or 1.0
        result = {name: value / total for name, value in raw.items()}
        # Cap concentration. Re-normalize the remainder until stable.
        for _ in range(len(result) + 1):
            capped = {k: min(v, self.ceiling) for k, v in result.items()}
            excess = sum(result[k] - capped[k] for k in result)
            free = [k for k, v in capped.items() if v < self.ceiling - 1e-12]
            if excess <= 1e-12 or not free:
                result = capped
                break
            add = excess / len(free)
            result = {k: (v + add if k in free else v) for k, v in capped.items()}
            total = sum(result.values())
            result = {k: v / total for k, v in result.items()}
        return result

    def weight(self, specialist: str) -> float:
        return self._raw_weight(specialist)
