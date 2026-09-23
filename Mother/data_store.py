from __future__ import annotations
from collections import deque

class HiveDataStore:
    def __init__(self, max_records: int = 500):
        self.discoveries = deque(maxlen=max_records)
        self.known_hazards = []
        self.explored_regions = set()
        self.be_history = {}

    def add_discovery(self, discovery: dict) -> bool:
        discovery_id = discovery.get("discovery_id")
        if any(d.get("discovery_id") == discovery_id for d in self.discoveries):
            return False
        self.discoveries.append(discovery)
        self.explored_regions.add(
            (round(discovery.get("x", 0) / 50), round(discovery.get("y", 0) / 50))
        )
        if discovery.get("hazard"):
            self.known_hazards.append(discovery)
        return True

    def snapshot(self) -> dict:
        return {
            "discoveries": list(self.discoveries),
            "known_hazards": list(self.known_hazards),
            "explored_regions": list(self.explored_regions),
        }
