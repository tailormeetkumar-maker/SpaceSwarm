"""Mission environment and deterministic external phenomena."""

from dataclasses import dataclass
import random


@dataclass
class Environment:
    width: float
    height: float
    rng: random.Random

    def damage_near_hazard(self, bees, probability: float) -> list[str]:
        affected = []
        for bee in bees:
            if not bee.alive:
                continue
            if self.rng.random() < probability:
                bee.apply_damage(self.rng.uniform(3.0, 18.0))
                affected.append(bee.bee_id)
        return affected
