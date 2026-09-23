# Simulation notes

The simulation is deliberately separated from the visualizer.

`Simulation.step()` is the source of truth. The Pygame layer only reads state and events.

This makes it possible later to:
- run thousands/millions of agents without rendering every one
- export event traces to CSV/JSON
- build a web dashboard
- benchmark communication protocols
- compare algorithms
- train ML models on simulation data
