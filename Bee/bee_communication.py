"""Same-hive local communication logic."""

import math
from Shared.messages import Message, MessageType, Observation


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def reachable_bees(bee, peers, comm_range: float):
    return [
        peer
        for peer in peers
        if peer.alive
        and peer.bee_id != bee.bee_id
        and peer.hive_id == bee.hive_id
        and distance(bee.position, peer.position) <= comm_range
    ]


def build_observation_message(bee, observation: Observation, receiver_id: str, step: int):
    return Message(
        sender_id=bee.bee_id,
        receiver_id=receiver_id,
        hive_id=bee.hive_id,
        message_type={
            "SCIENCE": MessageType.SCIENCE,
            "HAZARD": MessageType.HAZARD,
            "ENVIRONMENT": MessageType.DISCOVERY,
        }.get(observation.data_type.value, MessageType.DISCOVERY),
        payload={
            "observation": {
                "observation_id": observation.observation_id,
                "observer_id": observation.observer_id,
                "data_type": observation.data_type.value,
                "position": observation.position,
                "value": observation.value,
                "confidence": observation.confidence,
                "step": observation.step,
            }
        },
        step=step,
    )
