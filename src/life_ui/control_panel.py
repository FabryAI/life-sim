from __future__ import annotations
import pygame
import numpy as np
from dataclasses import dataclass
from life_sim.config import SimConfig

@dataclass
class Tunables:
    width: int
    height: int
    initial_agents: int
    initial_food_mean: float
    initial_food_flat: bool
    resource_regen_rate: float
    tick_rate_hz: int
    time_unit: str
    initial_age_median_years: float
    initial_age_spread_years: float
    initial_infected_pct: float
    # visual conflitto
    show_conflict_flash: bool
    conflict_flash_duration_s: float

    @classmethod
    def from_cfg(cls, cfg: SimConfig) -> "Tunables":
        return cls(
            width=cfg.width,
            height=cfg.height,
            initial_agents=cfg.initial_agents,
            initial_food_mean=cfg.initial_food_mean,
            initial_food_flat=cfg.initial_food_flat,
            resource_regen_rate=cfg.resource_regen_rate,
            tick_rate_hz=cfg.tick_rate_hz,
            time_unit=cfg.time_unit,
            initial_age_median_years=cfg.initial_age_median_years,
            initial_age_spread_years=cfg.initial_age_spread_years,
            initial_infected_pct=cfg.initial_infected_pct,
            show_conflict_flash=cfg.show_conflict_flash,
            conflict_flash_duration_s=cfg.conflict_flash_duration_s,
        )

    def to_cfg(self, seed: int = 42, toroidal: bool = True) -> SimConfig:
        return SimConfig(
            seed=seed, width=self.width, height=self.height, toroidal=toroidal,
            initial_agents=self.initial_agents,
            tick_rate_hz=self.tick_rate_hz,
            resource_regen_rate=self.resource_regen_rate,
            initial_food_mean=self.initial_food_mean, initial_food_flat=self.initial_food_flat,
            time_unit=self.time_unit,
            initial_age_median_years=self.initial_age_median_years,
            initial_age_spread_years=self.initial_age_spread_years,
            initial_infected_pct=self.initial_infected_pct,
            show_conflict_flash=self.show_conflict_flash,
            conflict_flash_duration_s=self.conflict_flash_duration_s,
        )

class ControlPanel:
    def __init__(self, tun: Tunables, font_name: str | None = None):
        self.tun = tun
        self.font_name = font_name
        self.options = [
            ("Larghezza griglia", "width", 64, 4096, 64),
            ("Altezza griglia", "height", 64, 4096, 64),
            ("Popolazione iniziale", "initial_agents", 0, 20000, 100),
            ("Cibo iniziale (media)", "initial_food_mean", 0.0, 1.0, 0.05),
            ("Cibo iniziale piatto", "initial_food_flat", False, True, 1),
            ("Rigenerazione cibo", "resource_regen_rate", 0.0, 0.2, 0.002),
            ("Tick rate (Hz)", "tick_rate_hz", 1, 240, 1),
            ("Time frame", "time_unit", 0, 0, 1),  # speciale

            ("Età mediana iniziale", "initial_age_median_years", 0.0, 80.0, 1.0),
            ("Deviazione età iniziale", "initial_age_spread_years", 0.0, 30.0, 0.5),
            ("Infetti iniziali (%)", "initial_infected_pct", 0.0, 1.0, 0.01),

            ("Mostra flash conflitto", "show_conflict_flash", False, True, 1),
            ("Durata flash (s)", "conflict_flash_duration_s", 0.1, 5.0, 0.1),
        ]
        self.index = 0

    def adjust(self, dir: int):
        label, field, lo, hi, step = self.options[self.index]
        val = getattr(self.tun, field)
        if field == "time_unit":
            order = ["year", "month", "day"]
            idx = order.index(self.tun.time_unit)
            self.tun.time_unit = order[(idx + dir) % len(order)]
            return
        if isinstance(lo, bool):
            setattr(self.tun, field, not val)
            return
        if isinstance(lo, int):
            nv = int(np.clip(val + dir * step, lo, hi))
        else:
            nv = float(np.clip(val + dir * step, lo, hi))
            nv = round(nv, 3)
        setattr(self.tun, field, nv)

    def move(self, dir: int):
        self.index = (self.index + dir) % len(self.options)

    def render(self, surf: pygame.Surface, win_rect: tuple[int,int,int,int]):
        x, y, w, h = win_rect
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (x, y))

        panel_w, panel_h = 640, 520
        px = x + (w - panel_w)//2
        py = y + (h - panel_h)//2
        pygame.draw.rect(surf, (28, 32, 38), (px, py, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(surf, (80, 80, 90), (px, py, panel_w, panel_h), 1, border_radius=8)

        title = pygame.font.SysFont(self.font_name, 22, bold=True).render("Pannello di controllo", True, (240,240,250))
        surf.blit(title, (px + 16, py + 12))

        font = pygame.font.SysFont(self.font_name, 18)
        info = [
            "↑/↓ seleziona  •  ←/→ modifica",
            "ENTER: Applica  •  ESC: Chiudi",
            "Nota: dimensioni/popolazione/cibo iniziale richiedono reset del mondo",
        ]
        for i, line in enumerate(info):
            surf.blit(font.render(line, True, (210,210,220)), (px + 16, py + 44 + i*20))

        ox, oy = px + 16, py + 110
        for i, (label, field, lo, hi, step) in enumerate(self.options):
            is_sel = (i == self.index)
            val = getattr(self.tun, field)
            display_val = val
            if field == "time_unit":
                display_val = {"year": "Anno", "month": "Mese", "day": "Giorno"}[self.tun.time_unit]
            if isinstance(lo, bool):
                display_val = "ON" if val else "OFF"
            color = (255,255,255) if is_sel else (205,205,215)
            s = f"{label}: {display_val}"
            surf.blit(font.render(s, True, color), (ox, oy + i*28))
