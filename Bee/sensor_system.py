"""Synthetic scientific/environmental sensors.

The values are deliberately structured so the simulation can be measured,
reproduced and analysed instead of being random animation data.
"""

from dataclasses import dataclass
import random

from Shared.messages import DataType, Observation


@dataclass
class SensorSystem:
    rng: random.Random
    discovery_probability: float
    hazard_probability: float

    def scan(
        self,
        bee_id: str,
        hive_id: str,
        position: tuple[float, float],
        step: int,
    ) -> list[Observation]:
        observations: list[Observation] = []

        if self.rng.random() < self.discovery_probability:
            strength = round(self.rng.uniform(0.35, 1.0), 3)
            observations.append(
                Observation(
                    observer_id=bee_id,
                    hive_id=hive_id,
                    data_type=DataType.SCIENCE,
                    position=position,
                    value={
                        "signal_strength": strength,
                        "spectral_band": self.rng.choice(["A", "B", "C", "D"]),
                        "temperature_k": round(self.rng.uniform(160, 420), 2),
                        "composition_hint": self.rng.choice(
                            ["ice", "silicate", "metallic", "volatile"]
                        ),
                    },
                    confidence=round(self.rng.uniform(0.65, 0.99), 3),
                    step=step,
                )
            )

        if self.rng.random() < self.hazard_probability:
            severity = round(self.rng.uniform(0.2, 1.0), 3)
            observations.append(
                Observation(
                    observer_id=bee_id,
                    hive_id=hive_id,
                    data_type=DataType.HAZARD,
                    position=position,
                    value={
                        "severity": severity,
                        "hazard": self.rng.choice(
                            ["radiation", "debris", "thermal", "unknown"]
                        ),
                    },
                    confidence=round(self.rng.uniform(0.70, 0.99), 3),
                    step=step,
                )
            )

        return observations
