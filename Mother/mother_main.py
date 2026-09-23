from __future__ import annotations
from collections import deque
from math import hypot
from random import uniform
from Bee.bee_main import Bee
from Mother.hive_manager import HiveManager
from Mother.data_store import HiveDataStore
from Mother.mother_algorithm import MotherAlgorithm
from Mother.earth_communication import MotherEarthCommunication
from Mother.bee_communication import MotherBeeCommunication
from Shared.config import CONFIG
from Shared.messages import Message, MessageType

class Mother:
    def __init__(self, earth, hive_id: str, mother_id: str, position: tuple[float, float], config=CONFIG):
        self.earth = earth
        self.hive_id = hive_id
        self.mother_id = mother_id
        self.position = position
        self.config = config
        self.time = 0.0
        self.inbox = deque()
        self.pending_earth_reports = deque()
        self.bee_health = {}
        self.bee_status = {}
        self.priority_discovery = None
        self.replacements_launched = 0

        self.data_store = HiveDataStore()
        self.hive_manager = HiveManager(self)
        self.algorithm = MotherAlgorithm(self)
        self.earth_comm = MotherEarthCommunication(self)
        self.bee_comm = MotherBeeCommunication(self)
        self.bees: dict[str, Bee] = {}
        self._next_bee_number = 1

    def initialize_bees(self, count: int) -> None:
        for _ in range(count):
            self.spawn_bee(replacement=False)

    def spawn_bee(self, replacement: bool = True):
        bee_id = f"{self.hive_id}-B{self._next_bee_number:04d}"
        self._next_bee_number += 1
        bee = Bee(
            mother=self,
            bee_id=bee_id,
            position=(
                self.position[0] + uniform(-120, 120),
                self.position[1] + uniform(-120, 120),
            ),
            inherited_state=self.data_store.snapshot(),
            replacement=replacement,
        )
        self.bees[bee_id] = bee
        self.hive_manager.add_bee(bee)
        if replacement:
            self.replacements_launched += 1
        return bee

    def deploy_replacements(self, count: int) -> None:
        capacity = self.config.MAX_BEES_PER_HIVE - self.hive_manager.alive_count
        for _ in range(max(0, min(count, capacity))):
            self.spawn_bee(replacement=True)

    def receive_from_earth(self, message: Message) -> bool:
        return self.earth_comm.receive_from_earth(message)

    def update(self, dt: float) -> None:
        self.time += dt
        self.algorithm.update(dt)

    @staticmethod
    def distance(a, b):
        return hypot(a[0] - b[0], a[1] - b[1])
