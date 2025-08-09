from __future__ import annotations
from .world import World
from .agent import Agent
from .systems.resources import step_resources
from .systems.movement import step_movement
from .systems.foraging import step_foraging
from .systems.aging import step_aging
from .systems.disease import step_disease
from .systems.conflict import step_conflict
from .systems.reproduction import step_reproduction
from .systems.mortality import step_mortality

def step(world: World, agents: list[Agent]) -> tuple[list[Agent], dict]:
    # ambiente
    step_resources(world)

    # agenti
    step_movement(world, agents)
    step_foraging(world, agents)
    step_aging(world.cfg, agents)
    _ = step_disease(world, agents)

    # conflitto
    agents, deaths_conflict, attempts_conflict, conflict_pos = step_conflict(world, agents)

    # riproduzione + mortalità
    agents, births = step_reproduction(world, agents)
    agents, deaths = step_mortality(world, agents)

    deaths["conflict"] = deaths.get("conflict", 0) + deaths_conflict

    info = {
        "births": births,
        "deaths": deaths,
        "infected": sum(1 for a in agents if a.infected),
        "conflicts": attempts_conflict,
        "conflict_positions": conflict_pos,
    }
    return agents, info
