from __future__ import annotations
from dataclasses import dataclass
from random import uniform

@dataclass
class SpaceObject:
    object_id: str
    x: float
    y: float
    object_type: str

class SpaceEnvironment:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.objects: list[SpaceObject] = []

    def generate_objects(self, count: int = 20) -> None:
        types = ["ASTEROID_FIELD", "ICE_REGION", "MINERAL_REGION", "UNKNOWN_REGION"]
        for i in range(count):
            self.objects.append(
                SpaceObject(
                    object_id=f"OBJ-{i+1:03d}",
                    x=uniform(50, self.width - 50),
                    y=uniform(50, self.height - 50),
                    object_type=types[i % len(types)],
                )
            )
