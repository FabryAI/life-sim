from __future__ import annotations
from typing import Iterable
from ..agent import Agent
from ..world import World

def step_movement(world: World, agents: list[Agent]) -> None:
    # Placeholder: jitter casuale minimo (da sostituire con logica di ricerca cibo)
    rng = world.rng.py
    w, h = world.cfg.width, world.cfg.height
    for a in agents:
        dx, dy = rng.choice([-1, 0, 1]), rng.choice([-1, 0, 1])
        a.x = (a.x + dx) % w if world.cfg.toroidal else max(0, min(w-1, a.x + dx))
        a.y = (a.y + dy) % h if world.cfg.toroidal else max(0, min(h-1, a.y + dy))
