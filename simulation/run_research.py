"""Command-line research run. No Pygame required."""
import json
from Shared.config import SimulationConfig
from simulation.simulator import SpaceSwarmSimulation

if __name__ == "__main__":
    sim = SpaceSwarmSimulation(config=SimulationConfig(), seed=7)
    report = sim.run(steps=500)
    print("\n=== SPACESWARM RESEARCH RUN ===")
    print(json.dumps(report, indent=2))
    print("\n=== RESEARCH METRICS ===")
    for k, v in report["metrics"].items():
        print(f"{k}: {v}")
    print("\n=== SAMPLE ACTUAL EVENTS ===")
    for event in sim.events[:30]:
        print(f"[{event.step:04d}] {event.event_type:<26} {event.actor} -> {event.target or '-'} | {event.details}")
