from __future__ import annotations
import numpy as np
from ..world import World

def step_resources(world: World) -> None:
    alpha = world.cfg.resource_regen_rate
    if world.cfg.compute_backend.lower() == "cupy":
        try:
            import cupy as cp
            d = cp.asarray(world.food)         # upload CPU -> GPU
            d += alpha * (1.0 - d)             # rigenerazione su GPU
            cp.clip(d, 0.0, 1.0, out=d)
            world.food = cp.asnumpy(d)         # download GPU -> CPU
        except Exception:
            # fallback CPU
            world.food += alpha * (1.0 - world.food)
            np.clip(world.food, 0.0, 1.0, out=world.food)
    else:
        world.food += alpha * (1.0 - world.food)
        np.clip(world.food, 0.0, 1.0, out=world.food)
