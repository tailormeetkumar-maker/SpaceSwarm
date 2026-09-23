from dataclasses import dataclass

@dataclass(frozen=True)
class SwarmConfig:
    WORLD_WIDTH: int = 1400
    WORLD_HEIGHT: int = 800

    HIVE_COUNT: int = 2
    INITIAL_BEES_PER_HIVE: int = 30
    MAX_BEES_PER_HIVE: int = 45

    COMMUNICATION_RADIUS: float = 145.0
    MOTHER_COMMUNICATION_RADIUS: float = 360.0
    MOTHER_REPORT_INTERVAL: float = 2.0

    BEE_SPEED_MIN: float = 25.0
    BEE_SPEED_MAX: float = 55.0
    SENSOR_RADIUS: float = 55.0

    DISCOVERY_PROBABILITY_PER_SECOND: float = 0.045
    REPLACEMENT_THRESHOLD: float = 0.72
    FAILURE_PROBABILITY_PER_SECOND: float = 0.003

    MAX_EVENT_HISTORY: int = 5000
    EARTH_FORWARD_INTERVAL: float = 1.0
    VISUAL_EVENT_LIFETIME: float = 1.5

CONFIG = SwarmConfig()
