from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time
import uuid

class MessageType(str, Enum):
    DISCOVERY = "DISCOVERY"
    DISCOVERY_RELAY = "DISCOVERY_RELAY"
    STATUS = "STATUS"
    HEALTH = "HEALTH"
    COMMAND = "COMMAND"
    HIVE_STATE = "HIVE_STATE"
    REPLACEMENT = "REPLACEMENT"
    ACK = "ACK"

@dataclass
class Message:
    sender_id: str
    receiver_id: str
    hive_id: str
    message_type: MessageType
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

@dataclass
class SimulationEvent:
    event_type: str
    source_id: str
    target_id: str | None
    hive_id: str | None
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
