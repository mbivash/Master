from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from master.core.contracts import MasterDecision, SpecialistForecast


class DecisionLog:
    """Append-only JSONL record of forecasts and decisions for later evaluation."""

    def __init__(self, path: str | Path = "data/decisions.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, forecasts: list[SpecialistForecast], decision: MasterDecision):
        event = {
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "forecasts": [asdict(f) | {"action": f.action.value} for f in forecasts],
            "decision": asdict(decision) | {"action": decision.action.value},
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, separators=(",", ":"), default=str) + "\n")
