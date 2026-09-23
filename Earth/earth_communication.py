from collections import deque
from Shared.messages import Message

class EarthCommunication:
    def __init__(self):
        self.inbox = deque()

    def receive_from_mother(self, message: Message) -> None:
        self.inbox.append(message)

    def receive_all(self) -> list[Message]:
        items = list(self.inbox)
        self.inbox.clear()
        return items

    def send_to_mother(self, mother, message: Message) -> bool:
        return mother.receive_from_earth(message)
