from __future__ import annotations
from collections import deque
from math import hypot
from random import choice, uniform
from Bee.bee_algorithm import BeeAlgorithm
from Bee.bee_communication import BeeCommunication
from Bee.mother_communication import BeeMotherCommunication
from Bee.sensor_system import SensorSystem
from Bee.navigation import Navigation
from Shared.config import CONFIG
from Shared.messages import Message

ROLES = [
    "COMMANDER", "EXPLORER", "SCIENTIST", "ENGINEER",
    "NAVIGATOR", "COMMUNICATOR", "SENSOR", "MEDICAL"
]

class Bee:
    def __init__(self, mother, bee_id: str, position, inherited_state=None,
                 replacement=True, config=CONFIG):
        self.mother = mother
        self.bee_id = bee_id
        self.hive_id = mother.hive_id
        self.position = position
        self.config = config
        self.alive = True
        self.replacement = replacement
        self.role = choice(ROLES)
        self.priority = None
        self.speed = uniform(config.BEE_SPEED_MIN, config.BEE_SPEED_MAX)
        self.battery = uniform(70, 100)
        self.local_inbox = deque()
        self.mother_inbox = deque()
        self.communication = BeeCommunication(self)
        self.mother_comm = BeeMotherCommunication(self)
        self.sensors = SensorSystem(self)
        self.navigation = Navigation(self)
        self.algorithm = BeeAlgorithm(self)
        self.inherited_state = inherited_state or {}

    def receive_from_bee(self, message: Message) -> bool:
        if message.hive_id != self.hive_id:
            return False
        self.local_inbox.append(message)
        return True

    def receive_from_mother(self, message: Message) -> bool:
        if message.hive_id != self.hive_id:
            return False
        self.mother_inbox.append(message)
        return True

    def distance_to_mother(self) -> float:
        return self.mother.distance(self.position, self.mother.position)

    def distance(self, a, b):
        return self.mother.distance(a, b)

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self.algorithm.update(dt)
        self.navigation.update(dt)
        self.battery = max(0, self.battery - dt * 0.12)
        if self.battery <= 0:
            self.alive = False
