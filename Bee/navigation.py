"""Local navigation: exploration with a soft attraction to the mother."""

import math
import random


def move(
    position: tuple[float, float],
    mother_position: tuple[float, float],
    world: tuple[float, float],
    rng: random.Random,
    step_size: float = 10.0,
) -> tuple[float, float]:
    x, y = position
    mx, my = mother_position

    dx, dy = mx - x, my - y
    distance = math.hypot(dx, dy)

    # Mostly explore locally; gently return toward the mother when far away.
    if distance > 260:
        pull = 0.45
    else:
        pull = 0.08

    angle = rng.uniform(0, 2 * math.pi)
    rx, ry = math.cos(angle), math.sin(angle)

    if distance > 0:
        tx, ty = dx / distance, dy / distance
    else:
        tx, ty = 0.0, 0.0

    vx = (1 - pull) * rx + pull * tx
    vy = (1 - pull) * ry + pull * ty
    norm = math.hypot(vx, vy) or 1.0

    nx = max(0.0, min(world[0], x + step_size * vx / norm))
    ny = max(0.0, min(world[1], y + step_size * vy / norm))
    return nx, ny
