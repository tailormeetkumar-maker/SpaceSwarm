from __future__ import annotations
from Shared.messages import Message, MessageType

class DataReceiver:
    def __init__(self):
        self.messages_received = 0
        self.discovery_archive: list[dict] = []

    def process(self, messages: list[Message]) -> list[dict]:
        new_discoveries = []
        for msg in messages:
            self.messages_received += 1
            if msg.message_type in (MessageType.DISCOVERY, MessageType.DISCOVERY_RELAY):
                discovery = dict(msg.payload)
                self.discovery_archive.append(discovery)
                new_discoveries.append(discovery)
        return new_discoveries
