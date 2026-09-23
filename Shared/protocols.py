from __future__ import annotations
from typing import Callable, Optional
from Shared.messages import Message

class EventBus:
    """Small in-process event bus. Replaceable later by TCP/UDP/network adapters."""

    def __init__(self):
        self._subscribers: list[Callable[[Message], None]] = []

    def subscribe(self, callback: Callable[[Message], None]) -> None:
        self._subscribers.append(callback)

    def publish(self, message: Message) -> None:
        for callback in tuple(self._subscribers):
            callback(message)

class CommunicationProtocol:
    """Abstract communication boundary used by agents."""

    def send(self, message: Message) -> bool:
        raise NotImplementedError

    def receive(self) -> list[Message]:
        raise NotImplementedError
