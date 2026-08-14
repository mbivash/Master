from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EdgeMonitor:
    """Tracks observed strategy returns and flags degrading edge."""

    window: int = 50
    degradation_threshold: float = 0.0
    _returns: dict[str, list[float]] = field(default_factory=dict)

    def record(self, strategy: str, return_fraction: float) -> None:
        values = self._returns.setdefault(strategy, [])
        values.append(return_fraction)
        if len(values) > self.window:
            del values[:-self.window]

    def expectancy(self, strategy: str) -> float:
        values = self._returns.get(strategy, [])
        return sum(values) / len(values) if values else 0.0

    def healthy(self, strategy: str) -> bool:
        values = self._returns.get(strategy, [])
        return len(values) < 10 or self.expectancy(strategy) > self.degradation_threshold

    def snapshot(self) -> dict[str, dict[str, float | bool | int]]:
        return {
            strategy: {
                "observations": len(values),
                "expectancy": self.expectancy(strategy),
                "healthy": self.healthy(strategy),
            }
            for strategy, values in self._returns.items()
        }
