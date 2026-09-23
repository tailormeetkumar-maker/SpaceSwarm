from __future__ import annotations
from Shared.messages import Message, MessageType
from random import random

class MotherAlgorithm:
    def __init__(self, mother):
        self.mother = mother
        self.last_report_time = 0.0

    def process_message(self, message: Message) -> None:
        if message.message_type in (MessageType.DISCOVERY, MessageType.DISCOVERY_RELAY):
            discovery = dict(message.payload)
            discovery["hive_id"] = self.mother.hive_id
            discovery["last_hop"] = message.sender_id
            if self.mother.data_store.add_discovery(discovery):
                self.mother.pending_earth_reports.append(discovery)

        elif message.message_type == MessageType.HEALTH:
            bee_id = message.payload.get("bee_id")
            self.mother.bee_health[bee_id] = message.payload

        elif message.message_type == MessageType.STATUS:
            bee_id = message.payload.get("bee_id")
            self.mother.bee_status[bee_id] = message.payload

        elif message.message_type == MessageType.COMMAND:
            if message.payload.get("command") == "INVESTIGATE_DISCOVERY":
                self.mother.priority_discovery = message.payload.get("discovery_id")

    def update(self, dt: float) -> None:
        while self.mother.inbox:
            self.process_message(self.mother.inbox.popleft())

        # Forward batched important discoveries to Earth.
        if self.mother.time - self.last_report_time >= self.mother.config.EARTH_FORWARD_INTERVAL:
            self.flush_reports()
            self.last_report_time = self.mother.time

        # Dynamic colony recovery.
        target = int(self.mother.config.INITIAL_BEES_PER_HIVE * self.mother.config.REPLACEMENT_THRESHOLD)
        if self.mother.hive_manager.alive_count < target:
            deficit = target - self.mother.hive_manager.alive_count
            self.mother.deploy_replacements(min(deficit, 3))

    def flush_reports(self) -> None:
        while self.mother.pending_earth_reports:
            discovery = self.mother.pending_earth_reports.popleft()
            message = Message(
                sender_id=self.mother.mother_id,
                receiver_id="EARTH",
                hive_id=self.mother.hive_id,
                message_type=MessageType.DISCOVERY,
                payload=discovery,
            )
            self.mother.earth_comm.send_to_earth(message)
