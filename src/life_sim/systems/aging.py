from __future__ import annotations
from ..agent import Agent
from ..config import years_per_tick, SimConfig

def step_aging(cfg: SimConfig, agents: list[Agent]) -> None:
    yp = years_per_tick(cfg)
    for a in agents:
        a.age_years += yp
        a.repro_cooldown_years = max(0.0, a.repro_cooldown_years - yp)
        # costo di mantenimento “annuo” distribuito per tick
        a.energy -= 0.3 * yp
