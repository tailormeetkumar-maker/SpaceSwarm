"""Core autonomous Bee agent.

This is the actual decision engine, not a visualizer. Each bee:
    1. observes its environment,
    2. updates local knowledge,
    3. decides what information is worth sharing,
    4. communicates only inside its own hive,
    5. reports telemetry to its own Mother,
    6. moves according to local navigation rules.

Roles are capabilities, not permanent identities. Mother can change them.
"""

from dataclasses import dataclass, field
import random

from Shared.config import SimulationConfig
from Shared.messages import DataType, Message, MessageType, Observation
from Bee.bee_communication import build_observation_message, reachable_bees
from Bee.mother_communication import heartbeat_message, telemetry_message
from Bee.navigation import move
from Bee.sensor_system import SensorSystem


ROLES = (
    "commander",
    "explorer",
    "scientist",
    "engineer",
    "navigator",
    "communicator",
    "sensor",
    "medical",
)


@dataclass
class Bee:
    bee_id: str
    hive_id: str
    mother_id: str
    position: tuple[float, float]
    role: str
    rng: random.Random
    config: SimulationConfig

    battery: float = 100.0
    health: float = 100.0
    alive: bool = True
    age: int = 0
    known_observation_ids: set[str] = field(default_factory=set)
    local_observations: dict[str, Observation] = field(default_factory=dict)
    last_decision: str = "initializing"
    messages_sent: int = 0
    messages_received: int = 0

    def __post_init__(self):
        self.sensor = SensorSystem(
            self.rng,
            self.config.discovery_probability,
            self.config.hazard_probability,
        )

    def step(self, step: int, mother_position, peers) -> tuple[list[Message], list[Observation], list[dict]]:
        if not self.alive:
            return [], [], []

        self.age += 1
        self.battery -= self.config.battery_drain_per_step

        observations = self.sensor.scan(
            self.bee_id, self.hive_id, self.position, step
        )

        outgoing: list[Message] = []
        decisions: list[dict] = []

        # Science/hazard observations are high-value information.
        for obs in observations:
            self.local_observations[obs.observation_id] = obs
            if obs.confidence >= 0.65:
                targets = reachable_bees(
                    self, peers, self.config.bee_comm_range
                )

                if targets:
                    # A communicator/scientist tends to share broadly;
                    # other roles send to a small local subset.
                    limit = len(targets) if self.role in {"scientist", "communicator"} else min(2, len(targets))
                    for peer in targets[:limit]:
                        outgoing.append(
                            build_observation_message(
                                self, obs, peer.bee_id, step
                            )
                        )
                        self.messages_sent += 1

                    self.known_observation_ids.add(obs.observation_id)
                    self.last_decision = f"share_{obs.data_type.value.lower()}"
                    decisions.append({
                        "action": "share_observation",
                        "observation_id": obs.observation_id,
                        "targets": [p.bee_id for p in targets[:limit]],
                        "confidence": obs.confidence,
                    })
                else:
                    self.last_decision = "store_locally_no_neighbor"
                    decisions.append({
                        "action": "store_locally",
                        "observation_id": obs.observation_id,
                    })

        # Heartbeats and telemetry are deliberately periodic.
        if step % self.config.heartbeat_interval == 0:
            outgoing.append(heartbeat_message(self, step))
            outgoing.append(telemetry_message(self, step))
            self.messages_sent += 2

        # Movement is always local; no global path planner is assumed.
        self.position = move(
            self.position,
            mother_position,
            (self.config.world_width, self.config.world_height),
            self.rng,
        )

        if self.battery <= 0 or self.health <= 0:
            self.alive = False
            self.last_decision = "shutdown"
            decisions.append({"action": "shutdown", "reason": "energy_or_health"})
        else:
            decisions.append({
                "action": "move_and_explore",
                "role": self.role,
                "battery": round(self.battery, 2),
            })

        return outgoing, observations, decisions

    def receive(self, message: Message) -> None:
        if not self.alive:
            return
        if message.hive_id != self.hive_id:
            return

        self.messages_received += 1

        if message.message_type == MessageType.RELAY:
            original = message.payload.get("original", {})
            obs = original.get("payload", {}).get("observation")
            if obs and obs.get("observation_id"):
                self.known_observation_ids.add(obs["observation_id"])
        elif message.message_type in {
            MessageType.SCIENCE,
            MessageType.HAZARD,
            MessageType.DISCOVERY,
        }:
            obs = message.payload.get("observation")
            if obs and obs.get("observation_id"):
                self.known_observation_ids.add(obs["observation_id"])
        elif message.message_type == MessageType.ROLE_UPDATE:
            new_role = message.payload.get("role")
            if new_role in ROLES:
                self.role = new_role
                self.last_decision = f"role_changed_to_{new_role}"
        elif message.message_type == MessageType.COMMAND:
            command = message.payload.get("command")
            self.last_decision = f"command_{command}"

    def apply_damage(self, amount: float) -> None:
        self.health = max(0.0, self.health - amount)
        if self.health <= 0:
            self.alive = False
            self.last_decision = "failed_health"
