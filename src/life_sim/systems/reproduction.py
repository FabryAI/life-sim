from __future__ import annotations
import random
from collections import defaultdict
from ..agent import Agent
from ..world import World
from ..config import years_per_tick

def step_reproduction(world: World, agents: list[Agent]) -> tuple[list[Agent], int]:
    cfg = world.cfg
    yp = years_per_tick(cfg)
    rng: random.Random = world.rng.py

    # bucket per cella: così troviamo incontri M-F
    cells = defaultdict(list)
    for a in agents:
        cells[(a.x, a.y)].append(a)

    newborns = 0
    new_agents: list[Agent] = []

    next_id = (max((a.id for a in agents), default=-1) + 1)

    for (x, y), group in cells.items():
        males = [a for a in group if a.sex == "M"]
        females = [a for a in group if a.sex == "F"]

        if not males or not females:
            continue

        # Abbiniamo random una coppia alla volta (semplice)
        rng.shuffle(males)
        rng.shuffle(females)
        for m, f in zip(males, females):
            # condizioni
            if (m.age_years >= cfg.maturity_age_years and
                f.age_years >= cfg.maturity_age_years and
                m.energy >= cfg.reproduction_energy_min and
                f.energy >= cfg.reproduction_energy_min and
                m.repro_cooldown_years <= 0.0 and
                f.repro_cooldown_years <= 0.0):
                if rng.random() <= cfg.reproduction_prob_per_meeting:
                    # costo
                    m.energy -= cfg.reproduction_cost
                    f.energy -= cfg.reproduction_cost
                    m.repro_cooldown_years = cfg.reproduction_cooldown_years
                    f.repro_cooldown_years = cfg.reproduction_cooldown_years

                    # figlio
                    sex = "M" if rng.random() < 0.5 else "F"
                    child = Agent(
                        id=next_id, x=x, y=y, sex=sex,
                        energy=cfg.child_energy,
                        age_years=0.0,
                        max_age=(m.max_age + f.max_age)/2.0
                    )
                    next_id += 1
                    new_agents.append(child)
                    newborns += 1

    if new_agents:
        agents.extend(new_agents)
    return agents, newborns
