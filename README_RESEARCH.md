# SpaceSwarm — Actual Agent/Communication Core

This version is the **simulation/research layer**, not the game/visual layer.

## Communication hierarchy

```text
Bee <-> nearby Bee       (same hive only)
Bee <-> own Mother
Mother <-> Earth
```

Cross-hive Bee communication is rejected by the protocol.

## What a Bee actually does

Every simulation step:

1. Scan sensors.
2. Produce structured scientific/environmental observations.
3. Decide whether an observation is worth sharing.
4. Send messages to reachable same-hive peers.
5. Periodically send telemetry/heartbeat to its Mother.
6. Move using local navigation rules.
7. Update local knowledge and internal state.

## Data types

- Science observations
- Hazard observations
- Environmental discoveries
- Navigation state
- Health/telemetry
- Communication state

## Mother behavior

Mother:

- maintains membership,
- stores observations,
- aggregates telemetry,
- monitors failures,
- reallocates missing roles,
- commands bees,
- sends aggregated reports to Earth,
- deploys replacement bees when the hive falls below its resilience threshold.

## Fault tolerance

When a bee fails:

```text
failure
  -> Mother detects missing agent
  -> hive state updates
  -> critical roles are reallocated
  -> replacement can be deployed
  -> replacement inherits hive knowledge
```

## Run

From the SpaceSwarm directory:

```powershell
python simulation/run_research.py
```

No Pygame is required for this research run.

## Important

The visualizer should consume `SimulationEvent` objects from this engine.

It must **not invent communication events** merely for animation.


## Research metrics
The engine measures observation generation, delivery to Mother/Earth, delivery rates, routing hops, end-to-end latency, routing stalls, blocked messages, communication volume, failures, and replacement recovery. The event stream is the source of truth for a future visualizer.
