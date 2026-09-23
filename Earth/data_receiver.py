"""Earth-side receiver. Earth only sees Mother transmissions."""

from dataclasses import dataclass, field


@dataclass
class EarthDataReceiver:
    reports: list[dict] = field(default_factory=list)
    observations: dict[str, dict] = field(default_factory=dict)

    def receive(self, message) -> int:
        if message.receiver_id != "EARTH":
            return 0

        if message.message_type.value != "EARTH_REPORT":
            return 0

        self.reports.append(message.to_dict())
        count = 0
        for obs in message.payload.get("observations", []):
            if obs["observation_id"] not in self.observations:
                self.observations[obs["observation_id"]] = obs
                count += 1
        return count
