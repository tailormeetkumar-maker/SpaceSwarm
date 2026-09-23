"""Bee -> own Mother communication."""

from Shared.messages import Message, MessageType


def telemetry_message(bee, step: int) -> Message:
    return Message(
        sender_id=bee.bee_id,
        receiver_id=bee.mother_id,
        hive_id=bee.hive_id,
        message_type=MessageType.TELEMETRY,
        payload={
            "position": bee.position,
            "battery": round(bee.battery, 2),
            "health": round(bee.health, 2),
            "role": bee.role,
            "known_observations": len(bee.known_observation_ids),
        },
        step=step,
    )


def heartbeat_message(bee, step: int) -> Message:
    return Message(
        sender_id=bee.bee_id,
        receiver_id=bee.mother_id,
        hive_id=bee.hive_id,
        message_type=MessageType.HEARTBEAT,
        payload={"position": bee.position, "battery": round(bee.battery, 2)},
        step=step,
    )
