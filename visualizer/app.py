from __future__ import annotations
import pygame
from pygame.math import Vector2
from Shared.config import CONFIG

class SpaceSwarmApp:
    def __init__(self, simulation):
        pygame.init()
        self.sim = simulation
        self.screen = pygame.display.set_mode((CONFIG.WORLD_WIDTH, CONFIG.WORLD_HEIGHT))
        pygame.display.set_caption("SpaceSwarm — Hive Communication Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 16)
        self.small = pygame.font.SysFont("consolas", 12)
        self.running = True
        self.paused = False
        self.speed_multiplier = 1.0
        self.last_event_index = 0
        self.signal_lines = []
        self.flash_points = []
        self.log_lines = []

    def run(self):
        while self.running:
            real_dt = self.clock.tick(60) / 1000.0
            self.handle_events()

            if not self.paused:
                sim_dt = real_dt * self.speed_multiplier
                self.sim.step(sim_dt)

            self.consume_events()
            self.draw()

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_UP:
                    self.speed_multiplier = min(8.0, self.speed_multiplier * 2)
                elif event.key == pygame.K_DOWN:
                    self.speed_multiplier = max(0.25, self.speed_multiplier / 2)
                elif event.key == pygame.K_r:
                    self.__init__(type(self.sim)())

    def consume_events(self):
        for event in self.sim.events[self.last_event_index:]:
            if event.event_type in {"DISCOVERY", "EARTH_RECEIVED", "BEE_LOST", "REPLACEMENT_DEPLOYED"}:
                self.log_lines.append(
                    f"[{event.timestamp:6.1f}] {event.event_type:<20} "
                    f"{event.source_id} -> {event.target_id or '-'}"
                )
                self.log_lines = self.log_lines[-10:]

            if event.event_type == "BEE_LOST":
                self.flash_points.append([event.payload.get("x", 0), event.payload.get("y", 0), 1.0])
        self.last_event_index = len(self.sim.events)

    def draw(self):
        self.screen.fill((8, 12, 24))

        # World title
        self.text("SPACESWARM — AUTONOMOUS HIVE SIMULATION", 20, 15, 22)

        # Mothers and bees
        for mother in self.sim.mothers.values():
            mx, my = map(int, mother.position)
            pygame.draw.circle(self.screen, (230, 180, 70), (mx, my), 20)
            pygame.draw.circle(self.screen, (255, 220, 100), (mx, my), 28, 2)
            self.text(mother.hive_id, mx - 35, my + 30, 14)

            for bee in mother.bees.values():
                if not bee.alive:
                    continue
                x, y = map(int, bee.position)
                pygame.draw.circle(self.screen, (110, 210, 255), (x, y), 4)

                # Draw recent local communications from the event history.
                # Discovery relay paths are represented by a short-lived pulse.
                for other in mother.bees.values():
                    if other.alive and other.bee_id != bee.bee_id:
                        dx, dy = other.position[0] - bee.position[0], other.position[1] - bee.position[1]
                        if dx * dx + dy * dy <= self.sim.config.COMMUNICATION_RADIUS ** 2:
                            # Keep this subtle: the underlying algorithm is local-range based.
                            pass

        # Earth panel
        panel_x = 1000
        pygame.draw.rect(self.screen, (18, 24, 42), (panel_x, 0, 400, CONFIG.WORLD_HEIGHT))
        self.text("EARTH CONTROL", panel_x + 20, 20, 20)
        self.text(f"Sim time: {self.sim.time:7.1f}s", panel_x + 20, 55)
        self.text(f"Speed: {self.speed_multiplier:.2f}x", panel_x + 20, 78)
        self.text(f"Status: {'PAUSED' if self.paused else 'RUNNING'}", panel_x + 20, 101)

        y = 140
        for mother in self.sim.mothers.values():
            alive = mother.hive_manager.alive_count
            self.text(f"{mother.hive_id}  {mother.mother_id}  bees={alive}", panel_x + 20, y)
            self.text(f"discoveries={len(mother.data_store.discoveries)}", panel_x + 20, y + 20)
            y += 55

        y += 10
        self.text("EVENT LOG", panel_x + 20, y, 17)
        y += 28
        for line in self.log_lines[-10:]:
            self.text(line[:48], panel_x + 20, y, 11)
            y += 19

        y += 10
        self.text("CONTROLS", panel_x + 20, y, 15)
        self.text("SPACE  pause/resume", panel_x + 20, y + 23, 12)
        self.text("UP/DOWN  speed", panel_x + 20, y + 42, 12)
        self.text("R  restart", panel_x + 20, y + 61, 12)

        # Flash effects for failures.
        for point in self.flash_points:
            pygame.draw.circle(self.screen, (255, 80, 80), (int(point[0]), int(point[1])), 10, 2)
            point[2] -= 0.04
        self.flash_points[:] = [p for p in self.flash_points if p[2] > 0]

        pygame.display.flip()

    def text(self, value, x, y, size=16):
        font = self.font if size >= 16 else self.small
        self.screen.blit(font.render(str(value), True, (220, 230, 245)), (x, y))
