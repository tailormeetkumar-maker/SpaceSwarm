"""Central configuration for the research-oriented SpaceSwarm simulation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    world_width: float = 1000.0
    world_height: float = 700.0

    hives: int = 2
    bees_per_hive: int = 20
    max_bees_per_hive: int = 28

    bee_comm_range: float = 115.0
    mother_comm_range: float = 90.0

    initial_battery: float = 100.0
    battery_drain_per_step: float = 0.20
    communication_cost: float = 0.05
    discovery_cost: float = 0.10

    heartbeat_interval: int = 5
    knowledge_ttl_steps: int = 120

    discovery_probability: float = 0.035
    hazard_probability: float = 0.012
    failure_probability: float = 0.0015

    replacement_below_fraction: float = 0.70
    max_hops: int = 8
    step_seconds: float = 1.0
