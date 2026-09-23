"""Earth-side analysis and long-term mission knowledge."""

from collections import Counter


def summarize(receiver):
    observations = list(receiver.observations.values())
    types = Counter(obs["data_type"] for obs in observations)
    hazards = [o for o in observations if o["data_type"] == "HAZARD"]

    return {
        "unique_observations": len(observations),
        "by_type": dict(types),
        "hazards": len(hazards),
        "mean_confidence": (
            round(sum(o["confidence"] for o in observations) / len(observations), 3)
            if observations else 0.0
        ),
    }
