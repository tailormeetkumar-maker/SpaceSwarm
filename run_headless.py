from simulation.simulator import Simulation

if __name__ == "__main__":
    sim = Simulation()
    sim.run_for_seconds(30)

    print("\n=== SPACE SWARM SUMMARY ===")
    print(f"Simulation time: {sim.time:.1f}s")
    print(f"Hives: {len(sim.mothers)}")
    print(f"Bees: {sum(len(m.bees) for m in sim.mothers.values())}")
    print(f"Events: {len(sim.events)}")
    print(f"Earth discoveries: {len(sim.earth.discovery_archive)}")
    print(f"Earth messages received: {sim.earth.messages_received}")
    print(f"Replacements launched: {sum(m.replacements_launched for m in sim.mothers.values())}")
    print("\nRecent Earth discoveries:")
    for item in sim.earth.discovery_archive[-10:]:
        print(
            f"- {item['discovery_id']} | {item['type']} | "
            f"hive={item['hive_id']} | source={item['source_bee']} | "
            f"confidence={item['confidence']:.2f}"
        )
