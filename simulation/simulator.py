"""Research simulation engine with explicit store-and-forward routing and metrics."""

from collections import defaultdict
import math
import random

from Bee.bee_algorithm import Bee, ROLES
from Earth.earth_main import Earth
from Mother.mother_algorithm import Mother
from Shared.config import SimulationConfig
from Shared.messages import Message, MessageType, SimulationEvent, Observation
from Shared.protocols import allowed, validate_message
from simulation.failures import inject_random_failures


class SpaceSwarmSimulation:
    def __init__(self, config: SimulationConfig | None = None, seed: int = 42):
        self.config = config or SimulationConfig()
        self.rng = random.Random(seed)
        self.earth = Earth()
        self.step_number = 0
        self.events: list[SimulationEvent] = []
        self.mothers: dict[str, Mother] = {}
        self.bees: dict[str, Bee] = {}
        self.metrics = defaultdict(int)
        self.observation_meta: dict[str, dict] = {}
        self._create_hives()

    def _create_hives(self):
        roles = list(ROLES)
        for h in range(self.config.hives):
            hive_id = f"HIVE-{h+1:02d}"
            mother_id = f"M-{h+1:02d}"
            x = 180 + h * 640
            y = self.config.world_height / 2
            mother = Mother(mother_id, hive_id, (x, y), self.config, random.Random(self.rng.randint(0, 10**9)))
            self.mothers[mother_id] = mother
            for i in range(self.config.bees_per_hive):
                bee_id = f"B-{h+1:02d}-{i+1:03d}"
                bee = Bee(
                    bee_id=bee_id, hive_id=hive_id, mother_id=mother_id,
                    position=(x + self.rng.uniform(-80, 80), y + self.rng.uniform(-80, 80)),
                    role=roles[i % len(roles)], rng=random.Random(self.rng.randint(0, 10**9)), config=self.config,
                )
                self.bees[bee_id] = bee
                mother.register_bee(bee)

    def _kind(self, entity_id: str) -> str:
        if entity_id == "EARTH": return "earth"
        if entity_id in self.bees: return "bee"
        if entity_id in self.mothers: return "mother"
        return "unknown"

    def _record(self, event_type, actor, target=None, **details):
        self.events.append(SimulationEvent(self.step_number, event_type, actor, target, details))

    def _send(self, message: Message) -> bool:
        validate_message(message)
        sender_kind, receiver_kind = self._kind(message.sender_id), self._kind(message.receiver_id)
        if not allowed(sender_kind, receiver_kind, message.message_type):
            self._record("MESSAGE_BLOCKED", message.sender_id, message.receiver_id, message_type=message.message_type.value, reason="protocol_violation")
            self.metrics["blocked_messages"] += 1
            return False

        if sender_kind == "bee" and receiver_kind == "bee":
            sender, receiver = self.bees[message.sender_id], self.bees[message.receiver_id]
            if sender.hive_id != receiver.hive_id:
                self._record("MESSAGE_BLOCKED", sender.bee_id, receiver.bee_id, reason="cross_hive_communication")
                self.metrics["blocked_messages"] += 1
                return False
            distance = math.dist(sender.position, receiver.position)
            if distance > self.config.bee_comm_range:
                self._record("MESSAGE_BLOCKED", sender.bee_id, receiver.bee_id, reason="out_of_range", distance=round(distance, 2))
                self.metrics["blocked_messages"] += 1
                return False
            receiver.receive(message)
            self._record("BEE_TO_BEE", sender.bee_id, receiver.bee_id, message_type=message.message_type.value, message_id=message.message_id, hop=message.hop_count)
            self.metrics["bee_messages"] += 1
            return True

        if sender_kind == "bee" and receiver_kind == "mother":
            sender, mother = self.bees[message.sender_id], self.mothers[message.receiver_id]
            if sender.hive_id != mother.hive_id:
                self.metrics["blocked_messages"] += 1
                return False
            distance = math.dist(sender.position, mother.position)
            if distance > self.config.mother_comm_range:
                self._record("BEE_TO_MOTHER_MISSED", sender.bee_id, mother.mother_id, message_type=message.message_type.value, distance=round(distance, 2))
                self.metrics["missed_mother_messages"] += 1
                return False
            results = mother.receive(message, self.step_number)
            self._record("BEE_TO_MOTHER", sender.bee_id, mother.mother_id, message_type=message.message_type.value, message_id=message.message_id, hop=message.hop_count, results=results)
            self.metrics["mother_messages"] += 1
            if message.message_type in {MessageType.SCIENCE, MessageType.HAZARD, MessageType.DISCOVERY}:
                oid = message.payload.get("observation", {}).get("observation_id")
                if oid and oid in self.observation_meta and not self.observation_meta[oid].get("mother_step"):
                    self.observation_meta[oid]["mother_step"] = self.step_number
                    self.observation_meta[oid]["mother_hops"] = message.hop_count
                    self.metrics["observations_delivered_to_mother"] += 1
                    self._record("OBSERVATION_AT_MOTHER", sender.bee_id, mother.mother_id, observation_id=oid, hops=message.hop_count, latency=self.step_number - self.observation_meta[oid]["generated_step"])
            return True

        if sender_kind == "mother" and receiver_kind == "bee":
            mother, bee = self.mothers[message.sender_id], self.bees[message.receiver_id]
            if mother.hive_id != bee.hive_id:
                self.metrics["blocked_messages"] += 1
                return False
            bee.receive(message)
            self._record("MOTHER_TO_BEE", mother.mother_id, bee.bee_id, message_type=message.message_type.value)
            self.metrics["mother_to_bee_messages"] += 1
            return True

        if sender_kind == "mother" and receiver_kind == "earth":
            delivered = self.earth.receive(message)
            self._record("MOTHER_TO_EARTH", message.sender_id, "EARTH", message_type=message.message_type.value, new_observations=delivered)
            self.metrics["earth_reports"] += 1
            self.metrics["earth_observations"] += delivered
            for obs in message.payload.get("observations", []):
                oid = obs.get("observation_id")
                if oid in self.observation_meta and not self.observation_meta[oid].get("earth_step"):
                    self.observation_meta[oid]["earth_step"] = self.step_number
                    self.metrics["observations_delivered_to_earth"] += 1
                    self._record("OBSERVATION_AT_EARTH", message.sender_id, "EARTH", observation_id=oid, latency=self.step_number - self.observation_meta[oid]["generated_step"], routing_latency=self.step_number - self.observation_meta[oid].get("mother_step", self.step_number))
            return True
        return False

    def _route_observation(self, source: Bee, obs: Observation):
        """Store-and-forward one observation using only local same-hive links."""
        oid = obs.observation_id
        payload = {
            "observation": {
                "observer_id": obs.observer_id, "data_type": obs.data_type.value,
                "position": obs.position, "value": obs.value, "confidence": obs.confidence,
                "step": obs.step, "observation_id": oid,
            }
        }
        msg_type = MessageType.HAZARD if obs.data_type.value == "HAZARD" else MessageType.SCIENCE
        current = source
        visited = {source.bee_id}

        for hop in range(self.config.max_hops + 1):
            mother = self.mothers[current.mother_id]
            mother_distance = math.dist(current.position, mother.position)
            if mother_distance <= self.config.mother_comm_range:
                message = Message(current.bee_id, mother.mother_id, current.hive_id, msg_type, payload, self.step_number, ttl=self.config.max_hops-hop, hop_count=hop)
                if self._send(message):
                    self._record("ROUTE_DECISION", current.bee_id, mother.mother_id, observation_id=oid, action="deliver_to_mother", hop=hop, distance=round(mother_distance, 2))
                    return

            candidates = [
                b for b in self.bees.values()
                if b.alive and b.hive_id == current.hive_id and b.bee_id not in visited
                and math.dist(current.position, b.position) <= self.config.bee_comm_range
            ]
            closer = [b for b in candidates if math.dist(b.position, mother.position) < mother_distance]
            if not closer:
                self._record("ROUTE_STALLED", current.bee_id, mother.mother_id, observation_id=oid, hop=hop, distance=round(mother_distance, 2))
                self.metrics["routing_stalls"] += 1
                return
            nxt = min(closer, key=lambda b: math.dist(b.position, mother.position))
            message = Message(current.bee_id, nxt.bee_id, current.hive_id, msg_type, payload, self.step_number, ttl=self.config.max_hops-hop, hop_count=hop)
            if not self._send(message):
                return
            self._record("ROUTE_DECISION", current.bee_id, nxt.bee_id, observation_id=oid, action="forward_toward_mother", hop=hop, distance_to_mother=round(math.dist(nxt.position, mother.position), 2))
            visited.add(nxt.bee_id)
            current = nxt
            self.metrics["observation_forward_hops"] += 1

        self.metrics["routing_ttl_exhausted"] += 1

    def _relay_local_messages(self, outgoing: list[Message]):
        for message in outgoing:
            self._send(message)

    def _deliver_failed_bee_notifications(self):
        for mother in self.mothers.values():
            for bee in list(mother.manager.members.values()):
                if not bee.alive and bee.bee_id not in mother.manager.failed_bees:
                    mother.manager.mark_failed(bee.bee_id)
                    self._record("BEE_FAILURE", bee.bee_id, mother.mother_id, role=bee.role)
                    self.metrics["failures"] += 1

    def _replace_bees(self):
        for mother in self.mothers.values():
            if not mother.manager.needs_replacement():
                continue
            alive = len(mother.manager.alive_bees())
            total = len(mother.manager.members)
            roles = mother.manager.role_distribution()
            role = min(["explorer", "scientist", "navigator", "communicator", "sensor"], key=lambda r: roles.get(r, 0))
            bee_id = f"{mother.hive_id}-R{mother.manager.replacements_created + 1:03d}"
            bee = Bee(bee_id, mother.hive_id, mother.mother_id, mother.position, role, random.Random(self.rng.randint(0, 10**9)), self.config)
            bee.known_observation_ids.update(mother.store.observations.keys())
            self.bees[bee_id] = bee
            mother.register_bee(bee)
            mother.manager.replacements_created += 1
            self._record("REPLACEMENT_DEPLOYED", mother.mother_id, bee_id, alive_before=alive, total_before=total, inherited_observations=len(bee.known_observation_ids), role=role)
            self.metrics["replacements"] += 1
            self.metrics["replacement_inherited_observations"] += len(bee.known_observation_ids)

    def step(self):
        self.step_number += 1
        for bee in list(self.bees.values()):
            if not bee.alive:
                continue
            mother = self.mothers[bee.mother_id]
            peers = [b for b in self.bees.values() if b.alive and b.hive_id == bee.hive_id]
            outgoing, observations, decisions = bee.step(self.step_number, mother.position, peers)
            for obs in observations:
                self.observation_meta[obs.observation_id] = {"generated_step": self.step_number, "hive_id": obs.hive_id, "observer": obs.observer_id}
                self.metrics["observations_generated"] += 1
                self._record("OBSERVATION", bee.bee_id, None, data_type=obs.data_type.value, observation_id=obs.observation_id, confidence=obs.confidence, value=obs.value)
                self._route_observation(bee, obs)
            for decision in decisions:
                self._record("BEE_DECISION", bee.bee_id, None, **decision)
            self._relay_local_messages(outgoing)

        failed = inject_random_failures(list(self.bees.values()), self.config.failure_probability, self.rng)
        for bee_id in failed:
            self._record("FAILURE_INJECTED", bee_id, None)
        self._deliver_failed_bee_notifications()

        for mother in self.mothers.values():
            outgoing, events = mother.step(self.step_number)
            for event in events:
                self._record("MOTHER_DECISION", mother.mother_id, None, **event)
            for message in outgoing:
                self._send(message)
        self._replace_bees()

    def run(self, steps: int = 300):
        for _ in range(steps):
            self.step()
        return self.report()

    def report(self) -> dict:
        generated = self.metrics["observations_generated"]
        to_mother = self.metrics["observations_delivered_to_mother"]
        to_earth = self.metrics["observations_delivered_to_earth"]
        latencies = [m["earth_step"]-m["generated_step"] for m in self.observation_meta.values() if m.get("earth_step") is not None]
        route_latencies = [m["mother_step"]-m["generated_step"] for m in self.observation_meta.values() if m.get("mother_step") is not None]
        hops = [m["mother_hops"] for m in self.observation_meta.values() if m.get("mother_hops") is not None]
        return {
            "steps": self.step_number,
            "alive_by_hive": {m.hive_id: len(m.manager.alive_bees()) for m in self.mothers.values()},
            "earth": self.earth.summary(),
            "metrics": {**dict(self.metrics),
                "observation_delivery_to_mother_rate": round(to_mother / generated, 4) if generated else 0.0,
                "observation_delivery_to_earth_rate": round(to_earth / generated, 4) if generated else 0.0,
                "mean_end_to_end_latency_steps": round(sum(latencies)/len(latencies), 3) if latencies else 0.0,
                "mean_bee_to_mother_latency_steps": round(sum(route_latencies)/len(route_latencies), 3) if route_latencies else 0.0,
                "mean_hops_to_mother": round(sum(hops)/len(hops), 3) if hops else 0.0,
                "messages_per_generated_observation": round((self.metrics["bee_messages"] + self.metrics["mother_messages"]) / generated, 3) if generated else 0.0,
                "failure_recovery_events": self.metrics["replacements"],
            },
            "events": len(self.events),
            "blocked_messages": self.metrics["blocked_messages"],
            "replacements": self.metrics["replacements"],
        }
