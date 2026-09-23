# SpaceSwarm

A Python prototype/simulation of a self-organizing space exploration swarm.

## Architecture

- **Earth**: high-level mission control, data reception, analysis, and commands.
- **Mother**: hive coordinator, memory, filtering, health monitoring, replacement deployment.
- **Bee**: autonomous scout with sensors, navigation, local same-hive communication, and mother reporting.
- **Shared**: message/event schemas and configuration.
- **simulation**: environment, simulation engine, failures.
- **visualizer**: a Pygame UI that displays the *real simulation events*.

## Communication rules

1. Bees communicate only with bees in the same hive.
2. Bee-to-bee communication is local: only nearby bees can exchange messages.
3. Bees can communicate with their own mother.
4. Earth communicates with mothers, never directly with bees.
5. A discovery travels through the simulated communication system and is visible in the event log/UI.
6. Mother state can be inherited by replacement bees.

## Run

Python 3.10+ is recommended.

Install the only external dependency:

```bash
pip install pygame
```

Run the graphical simulator:

```bash
python run.py
```

Run a headless simulation:

```bash
python run_headless.py
```

The visualizer is intentionally simple/cartoon-like. It is a debugging and research visualization, not a separate fake animation layer: communication lines, discoveries, failures, replacements, and status panels are driven by actual simulation events.

## V1 scope

The prototype models:
- multiple independent hives
- mother + bees
- dynamic bee roles
- local relay communication
- discovery detection
- mother filtering/aggregation
- Earth reception
- failure and replacement
- inherited hive knowledge
- configurable simulation speed
- event log
- communication statistics

The physics are abstracted. This is a software/algorithm simulation, not a spacecraft flight-dynamics model.
