from __future__ import annotations
from uuid import uuid4
from Shared.messages import Message, MessageType

class BeeAlgorithm:
    def __init__(self, bee):
        self.bee = bee
        self.reported_discoveries = set()
        self.last_health_report = 0.0

    def update(self, dt: float) -> None:
        # Process messages from local bees.
        while self.bee.local_inbox:
            message = self.bee.local_inbox.popleft()
            self._process_local_message(message)

        # Process mother commands.
        while self.bee.mother_inbox:
            message = self.bee.mother_inbox.popleft()
            self._process_mother_message(message)

        discovery = self.bee.sensors.update(dt)
        if discovery:
            discovery["discovery_id"] = f"D-{uuid4().hex[:10]}"
            discovery["source_bee"] = self.bee.bee_id
            discovery["hive_id"] = self.bee.hive_id
            self._handle_discovery(discovery)

        self._send_health_if_needed()

    def _handle_discovery(self, discovery: dict) -> None:
        self.reported_discoveries.add(discovery["discovery_id"])

        # First notify local neighbors. In a real protocol this could be
        # multi-hop gossip, TTL-limited flooding, or a learned relay policy.
        nearby = self.bee.mother.hive_manager.nearby_same_hive(
            self.bee, self.bee.config.COMMUNICATION_RADIUS
        )
        self.bee.communication.relay_discovery(discovery, nearby)

        # Mother link is modeled separately. A bee reports directly if it
        # is within the mother link range; otherwise the local network can
        # carry the discovery and a neighbor near the mother can report it.
        if self.bee.distance_to_mother() <= self.bee.config.MOTHER_COMMUNICATION_RADIUS:
            msg = Message(
                sender_id=self.bee.bee_id,
                receiver_id=self.bee.mother.mother_id,
                hive_id=self.bee.hive_id,
                message_type=MessageType.DISCOVERY,
                payload=discovery,
            )
            self.bee.mother_comm.send_to_mother(msg)

    def _process_local_message(self, message: Message) -> None:
        if message.hive_id != self.bee.hive_id:
            return
        discovery_id = message.payload.get("discovery_id")
        if discovery_id and discovery_id not in self.reported_discoveries:
            self.reported_discoveries.add(discovery_id)
            # Relay once more only if this bee has a mother link.
            if self.bee.distance_to_mother() <= self.bee.config.MOTHER_COMMUNICATION_RADIUS:
                msg = Message(
                    sender_id=self.bee.bee_id,
                    receiver_id=self.bee.mother.mother_id,
                    hive_id=self.bee.hive_id,
                    message_type=MessageType.DISCOVERY_RELAY,
                    payload=message.payload,
                )
                self.bee.mother_comm.send_to_mother(msg)

    def _process_mother_message(self, message: Message) -> None:
        # High-level command only; no direct Earth-to-bee channel exists.
        if message.message_type == MessageType.COMMAND:
            self.bee.priority = message.payload.get("discovery_id")

    def _send_health_if_needed(self) -> None:
        if self.bee.mother.time - self.last_health_report < 5.0:
            return
        self.last_health_report = self.bee.mother.time
        msg = Message(
            sender_id=self.bee.bee_id,
            receiver_id=self.bee.mother.mother_id,
            hive_id=self.bee.hive_id,
            message_type=MessageType.STATUS,
            payload={
                "bee_id": self.bee.bee_id,
                "role": self.bee.role,
                "position": self.bee.position,
                "alive": self.bee.alive,
                "battery": round(self.bee.battery, 2),
            },
        )
        self.bee.mother_comm.send_to_mother(msg)
