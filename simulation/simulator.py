from __future__ import annotations
from random import uniform
from Shared.config import CONFIG
from Shared.messages import SimulationEvent
from Earth.earth_main import Earth
from Mother.mother_main import Mother
from simulation.environment import SpaceEnvironment
from simulation.failures import FailureSimulator

class Simulation:
    def __init__(self, config=CONFIG):
        self.config = config
        self.time = 0.0
        self.events: list[SimulationEvent] = []
        self.earth = Earth()
        self.environment = SpaceEnvironment(config.WORLD_WIDTH, config.WORLD_HEIGHT)
        self.environment.generate_objects(24)
        self.failure_simulator = FailureSimulator(config.FAILURE_PROBABILITY_PER_SECOND)
        self.mothers: dict[str, Mother] = {}

        spacing = config.WORLD_WIDTH / (config.HIVE_COUNT + 1)
        for i in range(config.HIVE_COUNT):
            hive_id = f"HIVE-{i+1:02d}"
            mother_id = f"M-{i+1:02d}"
            mother = Mother(
                earth=self.earth,
                hive_id=hive_id,
                mother_id=mother_id,
                position=(spacing * (i + 1), config.WORLD_HEIGHT / 2),
                config=config,
            )
            mother.initialize_bees(config.INITIAL_BEES_PER_HIVE)
            self.mothers[hive_id] = mother

        self.last_alive_counts = {h.hive_id: len(h.bees) for h in self.mothers.values()}

    def emit(self, event_type, source_id, target_id=None, hive_id=None, payload=None):
        event = SimulationEvent(
            event_type=event_type,
            source_id=source_id,
            target_id=target_id,
            hive_id=hive_id,
            payload=payload or {},
            timestamp=self.time,
        )
        self.events.append(event)
        if len(self.events) > self.config.MAX_EVENT_HISTORY:
            self.events = self.events[-self.config.MAX_EVENT_HISTORY:]
        return event

    def step(self, dt: float) -> None:
        dt = max(0.0, min(dt, 0.1))
        previous_discoveries = len(self.earth.discovery_archive)

        for mother in self.mothers.values():
            for bee in list(mother.bees.values()):
                if bee.alive:
                    before = len(mother.data_store.discoveries)
                    bee.update(dt)
                    after = len(mother.data_store.discoveries)
                    if after > before:
                        for d in list(mother.data_store.discoveries)[-after + before:]:
                            self.emit("DISCOVERY", d.get("source_bee", ""), mother.mother_id, mother.hive_id, d)

            mother.update(dt)

        self.failure_simulator.update(self, dt)

        discoveries = self.earth.update(list(self.mothers.values()))
        for d in discoveries:
            self.emit("EARTH_RECEIVED", "EARTH", None, d.get("hive_id"), d)

        for mother in self.mothers.values():
            alive = mother.hive_manager.alive_count
            if alive > self.last_alive_counts[mother.hive_id]:
                self.emit(
                    "REPLACEMENT_DEPLOYED",
                    mother.mother_id,
                    None,
                    mother.hive_id,
                    {"alive_count": alive},
                )
            self.last_alive_counts[mother.hive_id] = alive

        self.time += dt

    def run_for_seconds(self, seconds: float, dt: float = 0.05):
        steps = int(seconds / dt)
        for _ in range(steps):
            self.step(dt)
