from __future__ import annotations
import pygame
import numpy as np
from typing import Tuple, List
from life_sim.agent import Agent
from life_sim.config import SimConfig

MAP_BASE_W = 900
WINDOW_H = 720

def layout_for_cfg(cfg: SimConfig, left_w: int, right_w: int) -> Tuple[Tuple[int,int], Tuple[int,int,int,int]]:
    map_w = MAP_BASE_W
    map_h = int(MAP_BASE_W * (cfg.height / cfg.width))
    win_w = left_w + map_w + right_w
    win_h = max(WINDOW_H, map_h)
    map_rect = (left_w, (win_h - map_h)//2, map_w, map_h)
    return (win_w, win_h), map_rect

def food_surface(food: np.ndarray) -> pygame.Surface:
    vis = np.clip(food, 0.0, 1.0)
    rgb = (vis * 255.0).astype(np.uint8)
    rgb = np.repeat(rgb[:, :, None], 3, axis=2)
    rgb = np.transpose(rgb, (1, 0, 2))
    return pygame.surfarray.make_surface(rgb)

def age_tint(color_base: tuple[int,int,int], age_years: float, max_age: float) -> tuple[int,int,int]:
    r = 0.0 if max_age <= 0 else min(1.0, max(0.0, age_years / max_age))
    lum = 1.0 - 0.5 * r
    return (int(color_base[0]*lum), int(color_base[1]*lum), int(color_base[2]*lum))

def draw_agents(screen: pygame.Surface, agents: List[Agent], cfg: SimConfig,
                mx: int, my: int, mw: int, mh: int) -> None:
    sx = mw / cfg.width
    sy = mh / cfg.height
    base_size = max(2, int(min(sx, sy)))
    risk_size = max(4, base_size + 1)

    for a in agents:
        px = mx + int(a.x * sx)
        py = my + int(a.y * sy)

        base = (0, 255, 255) if a.sex == "M" else (255, 0, 255)
        col = age_tint(base, a.age_years, a.max_age)

        size = risk_size if a.at_risk_conflict else base_size
        rect = pygame.Rect(px, py, size, size)
        pygame.draw.rect(screen, col, rect)

        if a.at_risk_conflict:
            outer = rect.inflate(2, 2)
            pygame.draw.rect(screen, (0, 0, 0), outer, 2)        # bordo nero
            pygame.draw.rect(screen, (255, 120, 0), rect, 1)     # bordo arancione

def draw_conflict_flashes(screen: pygame.Surface, flashes: list[tuple[float,int,int]],
                          cfg: SimConfig, mx: int, my: int, mw: int, mh: int) -> None:
    """Disegna cerchi semi-trasparenti per i conflitti avvenuti di recente."""
    if not flashes:
        return
    sx = mw / cfg.width
    sy = mh / cfg.height
    r = max(6, int(1.2 * min(sx, sy) * 2))

    overlay = pygame.Surface((mw, mh), pygame.SRCALPHA)
    for (tleft, cx, cy) in flashes:
        px = int(cx * sx)
        py = int(cy * sy)
        alpha = int(60 + 120 * max(0.0, min(1.0, tleft / max(1e-6, cfg.conflict_flash_duration_s))))
        color = (255, 100, 0, alpha)
        pygame.draw.circle(overlay, color, (px, py), r, width=1)
    screen.blit(overlay, (mx, my))
