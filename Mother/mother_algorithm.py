"""Core Mother spacecraft logic.

Mother is an edge coordinator:
- maintains hive membership,
- aggregates local discoveries,
- detects missing/failed bees,
- redistributes capabilities,
- sends commands to its own bees,
- reports aggregated information to Earth.
"""

from dataclasses import dataclass, field
import random

from Mother.bee_communication import handle_message
from Mother.earth_communication import build_earth_report
from Mother.hive_manager import HiveManager
from Mother.data_store import HiveDataStore
from Shared.config import SimulationConfig
from Shared.messages import Message, MessageType


@dataclass
class Mother:
    mother_id: str
    hive_id: str
    position: tuple[float, float]
    config: SimulationConfig
    rng: random.Random

    store: HiveDataStore = field(default_factory=HiveDataStore)
    reported_observations: set[str] = field(default_factory=set)

    def __post_init__(self):
        self.manager = HiveManager(
            self.hive_id,
            self.config.max_bees_per_hive,
            self.config.replacement_below_fraction,
        )

    def register_bee(self, bee) -> None:
        self.manager.register(bee)

    def receive(self, message: Message, step: int) -> list[dict]:
        if message.hive_id != self.hive_id:
            return []

        if message.message_id in self.store.seen_messages:
            return []
        self.store.seen_messages.add(message.message_id)

        return handle_message(self, message)

    def step(self, step: int) -> tuple[list[Message], list[dict]]:
        events = []
        outgoing: list[Message] = []

        for bee in self.manager.alive_bees():
            if bee.battery < 10:
                outgoing.append(Message(
                    sender_id=self.mother_id,
                    receiver_id=bee.bee_id,
                    hive_id=self.hive_id,
                    message_type=MessageType.COMMAND,
                    payload={"command": "return_to_mother"},
                    step=step,
                ))
                events.append({
                    "kind": "command",
                    "bee": bee.bee_id,
                    "command": "return_to_mother",
                })

        role_changes = self.manager.redistribute_roles()
        for bee_id, role in role_changes:
            outgoing.append(Message(
                sender_id=self.mother_id,
                receiver_id=bee_id,
                hive_id=self.hive_id,
                message_type=MessageType.ROLE_UPDATE,
                payload={"role": role},
                step=step,
            ))
            events.append({
                "kind": "role_reallocation",
                "bee": bee_id,
                "role": role,
            })

        if step % 5 == 0:
            report = build_earth_report(self, step)
            if report:
                outgoing.append(report)
                events.append({
                    "kind": "earth_report",
                    "observations": len(report.payload["observations"]),
                })

        return outgoing, events
