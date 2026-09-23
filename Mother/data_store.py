"""Persistent in-memory hive knowledge.

The store is intentionally structured like a small edge database. It can later
be replaced by SQLite/Parquet/a real database without changing the algorithms.
"""

from dataclasses import dataclass, field

from Shared.messages import Observation


@dataclass
class HiveDataStore:
    observations: dict[str, Observation] = field(default_factory=dict)
    latest_telemetry: dict[str, dict] = field(default_factory=dict)
    seen_messages: set[str] = field(default_factory=set)
    hazards: dict[str, Observation] = field(default_factory=dict)

    def add_observation(self, obs: Observation) -> bool:
        if obs.observation_id in self.observations:
            return False
        self.observations[obs.observation_id] = obs
        if obs.data_type.value == "HAZARD":
            self.hazards[obs.observation_id] = obs
        return True

    def update_telemetry(self, bee_id: str, telemetry: dict) -> None:
        self.latest_telemetry[bee_id] = telemetry

    def summary(self) -> dict:
        return {
            "observations": len(self.observations),
            "hazards": len(self.hazards),
            "telemetry_agents": len(self.latest_telemetry),
        }
