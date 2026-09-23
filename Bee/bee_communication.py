from __future__ import annotations
from Shared.messages import Message, MessageType

class BeeCommunication:
    """Local, same-hive communication only."""

    def __init__(self, bee):
        self.bee = bee

    def broadcast(self, message: Message, nearby_bees: list) -> list[str]:
        delivered = []
        for other in nearby_bees:
            if other.hive_id != self.bee.hive_id or not other.alive:
                continue
            other.receive_from_bee(message)
            delivered.append(other.bee_id)
        return delivered

    def relay_discovery(self, discovery: dict, nearby_bees: list) -> list[str]:
        message = Message(
            sender_id=self.bee.bee_id,
            receiver_id="LOCAL",
            hive_id=self.bee.hive_id,
            message_type=MessageType.DISCOVERY_RELAY,
            payload=discovery,
        )
        return self.broadcast(message, nearby_bees)
