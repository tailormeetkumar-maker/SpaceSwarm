from __future__ import annotations
from collections import Counter

class MLAnalyzer:
    """
    Placeholder for future Earth-side ML.

    V1 intentionally uses explainable statistics rather than pretending a
    trained model exists. Later this class can host anomaly detection,
    clustering, novelty scoring, or learned prioritization.
    """

    def summarize(self, discoveries: list[dict]) -> dict:
        counts = Counter(d.get("type", "UNKNOWN") for d in discoveries)
        if not discoveries:
            return {"total": 0, "types": {}, "mean_confidence": 0.0}
        mean_conf = sum(float(d.get("confidence", 0.0)) for d in discoveries) / len(discoveries)
        return {
            "total": len(discoveries),
            "types": dict(counts),
            "mean_confidence": round(mean_conf, 3),
        }
