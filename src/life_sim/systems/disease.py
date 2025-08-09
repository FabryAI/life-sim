from __future__ import annotations
import random
from ..agent import Agent
from ..world import World
from ..config import years_per_tick

def _per_tick_prob(p_annual: float, yp: float) -> float:
    # converte probabilità annuale in probabilità per tick che dura yp anni
    return 1.0 - (1.0 - p_annual) ** yp

def step_disease(world: World, agents: list[Agent]) -> dict:
    cfg = world.cfg
    yp = years_per_tick(cfg)
    rng: random.Random = world.rng.py
    deaths_disease = 0

    for a in agents:
        # infezione
        if not a.infected:
            if rng.random() < _per_tick_prob(cfg.infection_annual_prob, yp):
                a.infected = True
                a.disease_years = 0.0
        else:
            # progresso malattia
            a.disease_years += yp
            a.energy -= cfg.disease_energy_loss_per_year * yp

            # recovery
            if a.disease_years >= cfg.disease_recovery_after_years:
                if rng.random() < _per_tick_prob(cfg.disease_recovery_annual_prob, yp):
                    a.infected = False
                    a.disease_years = 0.0

    return {"deaths_disease": deaths_disease}  # il conteggio finale avviene in mortality
