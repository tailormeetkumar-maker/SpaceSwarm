````markdown
# 🚀 SpaceSwarm

**SpaceSwarm** is a Python-based research simulation for **autonomous space exploration using cooperative swarms of small spacecraft.**

The system consists of multiple independent **hives**, where each hive contains one **Mother spacecraft** and multiple autonomous **Bee spacecraft**.

## 🛰️ Architecture

```text
                    🌍 Earth
                       │
                       │
                    Mother
                  /    |    \
                Bee   Bee   Bee
                 ↕     ↕     ↕
              Local Hive Communication
````

* 🌍 **Earth** — Mission control and data analysis
* 🛰️ **Mother** — Manages the hive and communicates with Earth
* 🐝 **Bee** — Autonomous exploration and sensing
* ⚙️ **Simulation** — Runs the swarm and communication system
* 🎨 **Visualizer** — Pygame visualization

## 📡 Communication

```text
Bee ↔ Bee
   ↓
Mother
   ↓
Earth
```

* Bees communicate only with nearby Bees in the **same hive**
* Bees can communicate with their own Mother
* Bees cannot communicate directly with Earth
* Cross-hive Bee communication is blocked
* Observations can be forwarded through multiple Bees to reach the Mother

## 🧠 Features

* Autonomous exploration
* Scientific observations
* Hazard detection
* Local swarm communication
* Multi-hop message routing
* Dynamic Bee roles
* Mother coordination
* Failure detection
* Replacement Bees
* Hive knowledge inheritance
* Earth reporting
* Communication and performance metrics

## 🌿 Branches

### `main`

The **actual research and simulation engine**.

Run:

```bash
python -m simulation.run_research
```

### `pygame-visualizer`

The **graphical visualization version**.

Run:

```bash
python run.py
```

## ⚙️ Requirements

* Python 3.10+
* pygame-ce

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🔬 Research Scope

SpaceSwarm focuses on:

**Autonomy • Communication • Swarm Intelligence • Fault Tolerance • Distributed Exploration**

Spacecraft physics, orbital mechanics, and real hardware communication are currently abstracted.
