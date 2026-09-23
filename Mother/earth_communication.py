"""Mother -> Earth reporting. Bees never call this module."""

from Shared.messages import Message, MessageType


def build_earth_report(mother, step: int) -> Message | None:
    new_items = [
        obs for obs in mother.store.observations.values()
        if obs.observation_id not in mother.reported_observations
    ]

    if not new_items:
        return None

    payload = {
        "hive_id": mother.hive_id,
        "report_step": step,
        "observations": [
            {
                "observation_id": obs.observation_id,
                "observer_id": obs.observer_id,
                "data_type": obs.data_type.value,
                "position": obs.position,
                "value": obs.value,
                "confidence": obs.confidence,
                "observed_step": obs.step,
            }
            for obs in new_items
        ],
        "hive_summary": mother.store.summary(),
        "alive_bees": len(mother.manager.alive_bees()),
        "roles": mother.manager.role_distribution(),
    }

    for obs in new_items:
        mother.reported_observations.add(obs.observation_id)

    return Message(
        sender_id=mother.mother_id,
        receiver_id="EARTH",
        hive_id=mother.hive_id,
        message_type=MessageType.EARTH_REPORT,
        payload=payload,
        step=step,
    )
