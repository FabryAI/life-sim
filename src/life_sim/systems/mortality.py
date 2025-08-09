from __future__ import annotations
import random
from ..agent import Agent
from ..world import World
from ..config import years_per_tick

def step_mortality(world: World, agents: list[Agent]) -> tuple[list[Agent], dict]:
    cfg = world.cfg
    yp = years_per_tick(cfg)
    rng: random.Random = world.rng.py

    deaths = {"starvation": 0, "age": 0, "disease": 0}
    alive: list[Agent] = []

    for a in agents:
        died = False

        # malattia – mortalità dopo soglia
        if a.infected and a.disease_years >= cfg.disease_mortality_after_years:
            p = 1.0 - (1.0 - cfg.disease_mortality_annual_prob) ** yp
            if rng.random() < p:
                deaths["disease"] += 1
                died = True

        if not died and a.energy <= 0.0:
            deaths["starvation"] += 1
            died = True

        if not died and a.age_years > a.max_age:
            deaths["age"] += 1
            died = True

        if not died:
            alive.append(a)

    return alive, deaths
