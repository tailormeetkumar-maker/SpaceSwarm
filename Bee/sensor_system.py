from __future__ import annotations
from random import random, choice, uniform

DISCOVERY_TYPES = [
    "ICE_SIGNATURE", "MINERAL_SIGNATURE", "UNKNOWN_OBJECT",
    "RADIATION_ANOMALY", "POSSIBLE_BIO_SIGNATURE", "MAGNETIC_ANOMALY"
]

class SensorSystem:
    def __init__(self, bee):
        self.bee = bee
        self.cooldown = uniform(1.0, 5.0)

    def update(self, dt: float):
        self.cooldown -= dt
        if self.cooldown > 0:
            return None
        self.cooldown = uniform(3.0, 8.0)

        if random() <= self.bee.config.DISCOVERY_PROBABILITY_PER_SECOND * 5:
            return {
                "type": choice(DISCOVERY_TYPES),
                "x": round(self.bee.position[0], 2),
                "y": round(self.bee.position[1], 2),
                "confidence": round(uniform(0.45, 0.99), 2),
                "hazard": random() < 0.12,
            }
        return None
