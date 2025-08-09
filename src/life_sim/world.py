from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .config import SimConfig
from .rng import RNG

@dataclass
class World:
    cfg: SimConfig
    rng: RNG
    food: np.ndarray  # float32 mappa risorse

    @classmethod
    def create(cls, cfg: SimConfig) -> "World":
        rng = RNG(cfg.seed)
        h, w = cfg.height, cfg.width
        if cfg.initial_food_flat:
            food = np.full((h, w), cfg.initial_food_mean, dtype=np.float32)
        else:
            # random intorno alla media, clamp in [0,1]
            base = rng.np.random((h, w))
            food = (0.5 * base + (cfg.initial_food_mean - 0.25)).astype(np.float32)
            np.clip(food, 0.0, 1.0, out=food)
        return cls(cfg=cfg, rng=rng, food=food)
