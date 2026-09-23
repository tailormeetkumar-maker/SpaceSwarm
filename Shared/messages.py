"""Typed messages and observations exchanged inside SpaceSwarm.

Important design rule:
    Bee <-> same-hive Bee
    Bee <-> own Mother
    Mother <-> Earth

A Bee never communicates directly with Earth or another hive.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import uuid


class MessageType(str, Enum):
    DISCOVERY = "DISCOVERY"
    SCIENCE = "SCIENCE"
    HAZARD = "HAZARD"
    TELEMETRY = "TELEMETRY"
    HEARTBEAT = "HEARTBEAT"
    RELAY = "RELAY"
    ACK = "ACK"
    COMMAND = "COMMAND"
    ROLE_UPDATE = "ROLE_UPDATE"
    HIVE_STATE = "HIVE_STATE"
    EARTH_REPORT = "EARTH_REPORT"
    REPLACEMENT_REQUEST = "REPLACEMENT_REQUEST"


class DataType(str, Enum):
    SCIENCE = "SCIENCE"
    ENVIRONMENT = "ENVIRONMENT"
    HAZARD = "HAZARD"
    NAVIGATION = "NAVIGATION"
    HEALTH = "HEALTH"
    COMMUNICATION = "COMMUNICATION"


@dataclass(slots=True)
class Observation:
    observer_id: str
    hive_id: str
    data_type: DataType
    position: tuple[float, float]
    value: dict[str, Any]
    confidence: float
    step: int
    observation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])


@dataclass(slots=True)
class Message:
    sender_id: str
    receiver_id: str
    hive_id: str
    message_type: MessageType
    payload: dict[str, Any]
    step: int
    ttl: int = 8
    hop_count: int = 0
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def forwarded(self, sender_id: str, receiver_id: str, step: int) -> "Message":
        return Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            hive_id=self.hive_id,
            message_type=MessageType.RELAY,
            payload={"original": self.to_dict()},
            step=step,
            ttl=max(0, self.ttl - 1),
            hop_count=self.hop_count + 1,
            message_id=self.message_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "hive_id": self.hive_id,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "step": self.step,
            "ttl": self.ttl,
            "hop_count": self.hop_count,
        }


@dataclass(slots=True)
class SimulationEvent:
    step: int
    event_type: str
    actor: str
    target: str | None
    details: dict[str, Any]
