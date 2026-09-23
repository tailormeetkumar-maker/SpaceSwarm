from Shared.messages import Message, MessageType

class BeeMotherCommunication:
    def __init__(self, bee):
        self.bee = bee

    def send_to_mother(self, message: Message) -> bool:
        if message.hive_id != self.bee.hive_id:
            return False
        return self.bee.mother.bee_comm.receive_from_bee(message)

    def receive(self) -> list[Message]:
        items = list(self.bee.mother_inbox)
        self.bee.mother_inbox.clear()
        return items
