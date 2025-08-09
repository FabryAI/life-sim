from __future__ import annotations
import numpy as np
from dataclasses import dataclass

@dataclass
class SpatialHash:
    cell: int = 16  # bucket size

    def key(self, x: int, y: int) -> tuple[int, int]:
        return (x // self.cell, y // self.cell)
