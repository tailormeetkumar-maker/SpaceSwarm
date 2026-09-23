from __future__ import annotations
from math import cos, sin
from random import uniform

class Navigation:
    def __init__(self, bee):
        self.bee = bee
        self.angle = uniform(0, 6.283185307)

    def update(self, dt: float) -> None:
        # Random-walk exploration with gentle attraction to the mother.
        if uniform(0, 1) < 0.04:
            self.angle += uniform(-1.2, 1.2)

        x, y = self.bee.position
        speed = self.bee.speed

        # Keep bees in an operational zone around their mother.
        dx = self.bee.mother.position[0] - x
        dy = self.bee.mother.position[1] - y
        dist2 = dx * dx + dy * dy
        if dist2 > 260 * 260:
            self.angle = __import__("math").atan2(dy, dx)

        x += cos(self.angle) * speed * dt
        y += sin(self.angle) * speed * dt

        w, h = self.bee.config.WORLD_WIDTH, self.bee.config.WORLD_HEIGHT
        x = max(15, min(w - 15, x))
        y = max(15, min(h - 15, y))
        self.bee.position = (x, y)
