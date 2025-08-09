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

        food = np.zeros((h, w), dtype=np.float32)

        if cfg.initial_food_flat:
            # Distribuzione piatta
            food.fill(cfg.initial_food_mean)
        else:
            # Creazione di macchie di vegetazione
            num_clusters = max(1, int((h * w) * cfg.initial_food_mean * 0.02))
            for _ in range(num_clusters):
                cx = rng.py.randrange(w)
                cy = rng.py.randrange(h)
                radius = rng.py.randint(3, 12)
                yy, xx = np.ogrid[:h, :w]
                mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2
                # Intensità casuale nella macchia
                patch_intensity = rng.py.uniform(
                    cfg.initial_food_mean * 0.5, 
                    min(1.0, cfg.initial_food_mean * 1.5)
                )
                food[mask] = np.clip(food[mask] + patch_intensity, 0.0, 1.0)

        return cls(cfg=cfg, rng=rng, food=food)
