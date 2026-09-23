"""Earth command channel.

In this simulation Earth sends commands to Mothers only.
"""


def mission_command(mother_id: str, command: str) -> dict:
    return {
        "sender": "EARTH",
        "receiver": mother_id,
        "command": command,
    }
