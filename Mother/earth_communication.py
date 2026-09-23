from Shared.messages import Message

class MotherEarthCommunication:
    def __init__(self, mother):
        self.mother = mother

    def send_to_earth(self, message: Message) -> None:
        self.mother.earth.communication.receive_from_mother(message)

    def receive_from_earth(self, message: Message) -> bool:
        if message.hive_id != self.mother.hive_id:
            return False
        self.mother.inbox.append(message)
        return True
