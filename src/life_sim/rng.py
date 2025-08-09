import random
import numpy as np

class RNG:
    def __init__(self, seed: int = 42):
        self.py = random.Random(seed)
        self.np = np.random.default_rng(seed)

    def reseed(self, seed: int) -> None:
        self.py.seed(seed)
        self.np = np.random.default_rng(seed)
