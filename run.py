from simulation.simulator import Simulation
from visualizer.app import SpaceSwarmApp

if __name__ == "__main__":
    simulation = Simulation()
    app = SpaceSwarmApp(simulation)
    app.run()
