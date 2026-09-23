from random import random

class FailureSimulator:
    def __init__(self, probability_per_second: float):
        self.probability_per_second = probability_per_second

    def update(self, simulation, dt: float) -> None:
        for mother in simulation.mothers.values():
            for bee in list(mother.bees.values()):
                if bee.alive and random() < self.probability_per_second * dt:
                    bee.alive = False
                    simulation.emit(
                        "BEE_LOST",
                        bee.bee_id,
                        mother.mother_id,
                        mother.hive_id,
                        {"reason": "simulated_failure", "x": bee.position[0], "y": bee.position[1]},
                    )
