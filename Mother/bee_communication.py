"""Mother-side handling of messages arriving from its own hive."""

from Shared.messages import MessageType
from Shared.messages import Observation


def extract_observation(message):
    payload = message.payload.get("observation")
    if not payload:
        return None

    return Observation(
        observer_id=payload["observer_id"],
        hive_id=message.hive_id,
        data_type=__import__("Shared.messages", fromlist=["DataType"]).DataType(
            payload["data_type"]
        ),
        position=tuple(payload["position"]),
        value=payload["value"],
        confidence=float(payload["confidence"]),
        step=int(payload["step"]),
        observation_id=payload["observation_id"],
    )


def handle_message(mother, message):
    if message.hive_id != mother.hive_id:
        return []

    if message.message_type in {
        MessageType.SCIENCE,
        MessageType.HAZARD,
        MessageType.DISCOVERY,
    }:
        obs = extract_observation(message)
        if obs and mother.store.add_observation(obs):
            return [{
                "kind": "new_observation",
                "observation_id": obs.observation_id,
                "observer": obs.observer_id,
                "data_type": obs.data_type.value,
                "confidence": obs.confidence,
            }]

    if message.message_type == MessageType.TELEMETRY:
        mother.store.update_telemetry(
            message.sender_id,
            message.payload,
        )

    return []
