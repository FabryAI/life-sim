from __future__ import annotations
from ..agent import Agent
from ..world import World

def step_foraging(world: World, agents: list[Agent]) -> None:
    th = getattr(world.cfg, "min_eat_to_count", 0.02)
    for a in agents:
        val = world.food[a.y, a.x]
        eat = min(0.1, float(val))
        if eat > 0.0:
            world.food[a.y, a.x] -= eat
            a.energy += eat * 5.0
            if eat >= th:
                a.ate_recent_ticks = 5
                a.hunger_streak_ticks = 0
            else:
                a.hunger_streak_ticks += 1
                if a.ate_recent_ticks > 0:
                    a.ate_recent_ticks -= 1
        else:
            a.hunger_streak_ticks += 1
            if a.ate_recent_ticks > 0:
                a.ate_recent_ticks -= 1
