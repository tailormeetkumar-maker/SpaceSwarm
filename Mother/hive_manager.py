"""Membership, health and role management for one hive."""

from collections import Counter


class HiveManager:
    def __init__(self, hive_id: str, max_bees: int, replacement_fraction: float):
        self.hive_id = hive_id
        self.max_bees = max_bees
        self.replacement_fraction = replacement_fraction
        self.members = {}
        self.failed_bees = set()
        self.replacements_created = 0

    def register(self, bee) -> None:
        self.members[bee.bee_id] = bee

    def alive_bees(self):
        return [b for b in self.members.values() if b.alive]

    def mark_failed(self, bee_id: str) -> None:
        self.failed_bees.add(bee_id)

    def needs_replacement(self) -> bool:
        alive = len(self.alive_bees())
        target = max(1, int(len(self.members) * self.replacement_fraction))
        return alive < target and len(self.members) < self.max_bees

    def role_distribution(self) -> dict[str, int]:
        return dict(Counter(b.role for b in self.alive_bees()))

    def redistribute_roles(self) -> list[tuple[str, str]]:
        """Fill missing critical capabilities after failures."""
        alive = self.alive_bees()
        if not alive:
            return []

        changes = []
        roles = self.role_distribution()

        critical = ["explorer", "scientist", "navigator", "communicator", "engineer"]
        for role in critical:
            if roles.get(role, 0) > 0:
                continue

            candidate = max(
                alive,
                key=lambda b: (b.battery, b.health, b.age),
            )
            if candidate.role != role:
                old = candidate.role
                candidate.role = role
                candidate.last_decision = f"reallocated_{old}_to_{role}"
                roles[role] = 1
                changes.append((candidate.bee_id, role))
        return changes
