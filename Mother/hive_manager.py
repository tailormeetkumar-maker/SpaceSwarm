from __future__ import annotations

class HiveManager:
    def __init__(self, mother):
        self.mother = mother
        self.members: dict[str, object] = {}

    def add_bee(self, bee) -> None:
        if bee.hive_id == self.mother.hive_id:
            self.members[bee.bee_id] = bee

    def remove_bee(self, bee_id: str) -> None:
        self.members.pop(bee_id, None)

    def nearby_same_hive(self, bee, radius: float) -> list:
        result = []
        for other in self.members.values():
            if other.bee_id == bee.bee_id or not other.alive:
                continue
            if self.mother.distance(bee.position, other.position) <= radius:
                result.append(other)
        return result

    @property
    def alive_count(self) -> int:
        return sum(1 for b in self.members.values() if b.alive)
