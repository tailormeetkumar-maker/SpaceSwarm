from __future__ import annotations
from Shared.messages import Message, MessageType

class EarthAlgorithm:
    """High-level mission logic. Earth does not micromanage individual bees."""

    def __init__(self):
        self.commands_sent = 0

    def evaluate(self, discoveries: list[dict], mothers: list) -> list[tuple[object, Message]]:
        commands = []
        for mother in mothers:
            # Example high-level adaptive command:
            # ask a hive to investigate when a novel/high-confidence discovery arrives.
            relevant = [d for d in discoveries if d.get("hive_id") == mother.hive_id]
            if relevant:
                best = max(relevant, key=lambda d: d.get("confidence", 0.0))
                msg = Message(
                    sender_id="EARTH",
                    receiver_id=mother.mother_id,
                    hive_id=mother.hive_id,
                    message_type=MessageType.COMMAND,
                    payload={
                        "command": "INVESTIGATE_DISCOVERY",
                        "discovery_id": best["discovery_id"],
                        "priority": "HIGH" if best["confidence"] >= 0.8 else "NORMAL",
                    },
                )
                commands.append((mother, msg))
                self.commands_sent += 1
        return commands
