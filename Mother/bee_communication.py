from __future__ import annotations
from Bee.bee_communication import BeeCommunication
from Shared.messages import Message, MessageType

class MotherBeeCommunication:
    def __init__(self, mother):
        self.mother = mother
        self.received_messages = 0

    def receive_from_bee(self, message: Message) -> bool:
        if message.hive_id != self.mother.hive_id:
            return False
        self.received_messages += 1
        self.mother.inbox.append(message)
        return True

    def send_to_bee(self, bee, message: Message) -> bool:
        if bee.hive_id != self.mother.hive_id:
            return False
        bee.receive_from_mother(message)
        return True
