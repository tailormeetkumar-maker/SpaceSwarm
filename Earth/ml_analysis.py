"""Analysis hooks.

This module intentionally does not pretend to have a trained ML model.
It provides clean feature extraction so a real model can later be trained
from simulation runs.
"""

def build_features(receiver):
    return [
        {
            "observation_id": obs["observation_id"],
            "confidence": obs["confidence"],
            "step": obs["observed_step"],
            "data_type": obs["data_type"],
            "x": obs["position"][0],
            "y": obs["position"][1],
        }
        for obs in receiver.observations.values()
    ]
