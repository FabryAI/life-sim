from __future__ import annotations
import random
from collections import defaultdict
from ..agent import Agent
from ..world import World

_NEIGHBORS = [(-1,-1), (0,-1), (1,-1),
              (-1, 0),         (1, 0),
              (-1, 1), (0, 1), (1, 1)]

def _wrap(x: int, w: int) -> int:
    return (x + w) % w

def _clamp(x: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, x))

def step_conflict(world: World, agents: list[Agent]) -> tuple[list[Agent], int, int, list[tuple[int,int]]]:
    """
    Ritorna: (agents_vivi, deaths_conflict, attempts_conflict, conflict_positions)
    Scenari:
      - Affamato (streak>=H) vicino a chi ha mangiato di recente -> p = conflict_kill_prob (+bonus)
      - Affamato (streak>=H) vicino ad altro affamato (streak>=H) -> p = conflict_kill_prob_hungry_pair
    Visual: setta a.at_risk_conflict quando stiamo valutando il conflitto.
    """
    cfg = world.cfg
    rng: random.Random = world.rng.py
    w, h = cfg.width, cfg.height

    for a in agents:
        a.at_risk_conflict = False

    cells = defaultdict(list)
    for a in agents:
        cells[(a.x, a.y)].append(a)

    deaths_conflict = 0
    attempts_conflict = 0
    conflict_positions: list[tuple[int,int]] = []
    alive: list[Agent] = []

    H = cfg.conflict_hunger_ticks

    for a in agents:
        if a.hunger_streak_ticks < H:
            alive.append(a)
            continue

        neighbor_has_eater = False
        neighbor_has_hungry = False
        neighbor_strong = False

        for dx, dy in _NEIGHBORS:
            nx = _wrap(a.x + dx, w) if cfg.toroidal else _clamp(a.x + dx, 0, w-1)
            ny = _wrap(a.y + dy, h) if cfg.toroidal else _clamp(a.y + dy, 0, h-1)
            for nb in cells.get((nx, ny), ()):
                if nb.ate_recent_ticks > 0:
                    neighbor_has_eater = True
                    if nb.energy >= cfg.conflict_strong_energy_thresh:
                        neighbor_strong = True
                if nb.hunger_streak_ticks >= H:
                    neighbor_has_hungry = True

        base_p = None
        if neighbor_has_eater:
            base_p = cfg.conflict_kill_prob
        elif neighbor_has_hungry:
            base_p = cfg.conflict_kill_prob_hungry_pair

        if base_p is None:
            alive.append(a)
            continue

        a.at_risk_conflict = True
        attempts_conflict += 1

        p = base_p
        if a.energy < cfg.conflict_weak_energy_thresh:
            p += cfg.conflict_bonus_if_weak
        if neighbor_has_eater and neighbor_strong:
            p += cfg.conflict_bonus_if_strong
        p = max(0.0, min(1.0, p))

        if rng.random() < p:
            deaths_conflict += 1
            conflict_positions.append((a.x, a.y))
        else:
            alive.append(a)

    return alive, deaths_conflict, attempts_conflict, conflict_positions
