"""Failure injection for resilience experiments."""

import random


def inject_random_failures(bees, probability: float, rng: random.Random) -> list[str]:
    failed = []
    for bee in bees:
        if bee.alive and rng.random() < probability:
            bee.apply_damage(1000)
            failed.append(bee.bee_id)
    return failed
