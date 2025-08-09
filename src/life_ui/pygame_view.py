from __future__ import annotations
import pygame
from collections import deque
from typing import Deque

from life_sim.config import SimConfig
from life_sim.world import World
from life_sim.agent import Agent
from life_sim.scheduler import step

from .renderer import layout_for_cfg, food_surface, draw_agents, draw_conflict_flashes
from .panels import draw_panel, draw_stats_panel, make_legend_lines
from .control_panel import Tunables, ControlPanel

LEFT_PANEL_W = 240
RIGHT_PANEL_W = 340
WINDOW_BG = (18, 18, 22)
FONT_NAME = None  # default di sistema


def init_agents(cfg: SimConfig, world: World) -> list[Agent]:
    rng = world.rng.py
    np_rng = world.rng.np
    agents: list[Agent] = []
    mu = cfg.initial_age_median_years
    sigma = max(0.0, cfg.initial_age_spread_years)
    for i in range(cfg.initial_agents):
        sex = "M" if rng.random() < 0.5 else "F"
        age = float(np_rng.normal(mu, sigma)) if sigma > 0 else mu
        age = max(0.0, min(age, 0.95 * 80.0))
        infected = (rng.random() < cfg.initial_infected_pct)
        agents.append(Agent(
            id=i, x=rng.randrange(cfg.width), y=rng.randrange(cfg.height),
            sex=sex, age_years=age, infected=infected
        ))
    return agents


def main() -> None:
    cfg = SimConfig()
    world = World.create(cfg)
    agents = init_agents(cfg, world)

    pygame.init()
    (win_w, win_h), map_rect = layout_for_cfg(cfg, LEFT_PANEL_W, RIGHT_PANEL_W)
    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    pygame.display.set_caption("Life-Sim")
    clock = pygame.time.Clock()

    bg = food_surface(world.food)
    bg_scaled = pygame.transform.smoothscale(bg, (map_rect[2], map_rect[3]))
    redraw_every = 5

    ticks = 0
    births_total = 0
    deaths_total = 0
    deaths_starv = deaths_age = deaths_disease = deaths_conflict = 0
    infected_now = 0
    conflicts_current = 0

    # flash conflitti (time_left_s, x_cell, y_cell)
    conflict_flashes: list[tuple[float,int,int]] = []

    # history
    H: int = 600
    hist_pop: Deque[int] = deque(maxlen=H)
    hist_male: Deque[int] = deque(maxlen=H)
    hist_fem: Deque[int] = deque(maxlen=H)
    hist_infected: Deque[int] = deque(maxlen=H)
    hist_births: Deque[int] = deque(maxlen=H)
    hist_deaths: Deque[int] = deque(maxlen=H)
    hist_dconf: Deque[int] = deque(maxlen=H)
    hist_conflicts: Deque[int] = deque(maxlen=H)
    hist_eavg: Deque[float] = deque(maxlen=H)
    hist_aavg: Deque[float] = deque(maxlen=H)

    paused = False
    speed_mult = 1.0
    tick_hz = cfg.tick_rate_hz
    fixed_dt = 1.0 / max(1, tick_hz)
    acc = 0.0

    show_ctrl = False
    tun = Tunables.from_cfg(cfg)
    ctrl = ControlPanel(tun, font_name=FONT_NAME)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.VIDEORESIZE:
                win_w, win_h = e.w, e.h
                screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
                mx, my, mw, mh = LEFT_PANEL_W, 0, max(100, win_w - (LEFT_PANEL_W + RIGHT_PANEL_W)), win_h
                target_h = int(mw * (cfg.height / cfg.width))
                if target_h > mh:
                    mw = int(mh * (cfg.width / cfg.height)); target_h = mh
                map_rect = (LEFT_PANEL_W, (win_h - target_h)//2, mw, target_h)
                bg_scaled = pygame.transform.smoothscale(bg, (map_rect[2], map_rect[3]))
            elif e.type == pygame.KEYDOWN:
                if show_ctrl:
                    if e.key == pygame.K_ESCAPE:
                        show_ctrl = False
                    elif e.key == pygame.K_RETURN:
                        new_cfg = tun.to_cfg(seed=cfg.seed, toroidal=cfg.toroidal)
                        need_reset = (
                            new_cfg.width != cfg.width or
                            new_cfg.height != cfg.height or
                            new_cfg.initial_agents != cfg.initial_agents or
                            new_cfg.initial_food_mean != cfg.initial_food_mean or
                            new_cfg.initial_food_flat != cfg.initial_food_flat or
                            new_cfg.time_unit != cfg.time_unit or
                            new_cfg.initial_age_median_years != cfg.initial_age_median_years or
                            new_cfg.initial_age_spread_years != cfg.initial_age_spread_years or
                            new_cfg.initial_infected_pct != cfg.initial_infected_pct
                        )
                        cfg = new_cfg
                        tick_hz = cfg.tick_rate_hz
                        fixed_dt = 1.0 / max(1, tick_hz)
                        if need_reset:
                            world = World.create(cfg)
                            agents = init_agents(cfg, world)
                            ticks = 0
                            births_total = deaths_total = 0
                            deaths_starv = deaths_age = deaths_disease = deaths_conflict = 0
                            infected_now = 0
                            conflicts_current = 0
                            conflict_flashes.clear()
                            for dq in (hist_pop, hist_male, hist_fem, hist_infected,
                                       hist_births, hist_deaths, hist_dconf, hist_conflicts,
                                       hist_eavg, hist_aavg):
                                dq.clear()
                            (win_w, win_h), map_rect = layout_for_cfg(cfg, LEFT_PANEL_W, RIGHT_PANEL_W)
                            screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
                            bg = food_surface(world.food)
                            bg_scaled = pygame.transform.smoothscale(bg, (map_rect[2], map_rect[3]))
                        show_ctrl = False
                    elif e.key == pygame.K_UP:
                        ctrl.move(-1)
                    elif e.key == pygame.K_DOWN:
                        ctrl.move(+1)
                    elif e.key == pygame.K_LEFT:
                        ctrl.adjust(-1)
                    elif e.key == pygame.K_RIGHT:
                        ctrl.adjust(+1)
                else:
                    if e.key == pygame.K_ESCAPE:
                        running = False
                    elif e.key == pygame.K_SPACE:
                        paused = not paused
                    elif e.key in (pygame.K_PLUS, pygame.K_EQUALS):
                        speed_mult = min(8.0, speed_mult * 2.0)
                    elif e.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                        speed_mult = max(0.25, speed_mult / 2.0)
                    elif e.key == pygame.K_c:
                        show_ctrl = True; paused = True

        dt = clock.tick(60) / 1000.0
        acc += dt * speed_mult

        # decay dei flash (anche in pausa)
        if conflict_flashes:
            tmp: list[tuple[float,int,int]] = []
            for (tleft, cx, cy) in conflict_flashes:
                nt = tleft - dt
                if nt > 0:
                    tmp.append((nt, cx, cy))
            conflict_flashes = tmp

        stepped = False
        while not paused and not show_ctrl and acc >= fixed_dt:
            agents, info = step(world, agents)
            ticks += 1
            births_total += info["births"]
            deaths_total += sum(info["deaths"].values())
            deaths_starv += info["deaths"]["starvation"]
            deaths_age += info["deaths"]["age"]
            deaths_disease += info["deaths"]["disease"]
            deaths_conflict += info["deaths"].get("conflict", 0)
            infected_now = info["infected"]
            conflicts_current = info.get("conflicts", 0)
            # flash nuovi
            dur = cfg.conflict_flash_duration_s
            for (cx, cy) in info.get("conflict_positions", []):
                conflict_flashes.append((dur, cx, cy))

            acc -= fixed_dt
            stepped = True

            # history
            m = sum(1 for a in agents if a.sex == "M")
            f = len(agents) - m
            e_avg = (sum(a.energy for a in agents)/len(agents)) if agents else 0.0
            a_avg = (sum(a.age_years for a in agents)/len(agents)) if agents else 0.0
            hist_pop.append(len(agents)); hist_male.append(m); hist_fem.append(f)
            hist_infected.append(infected_now)
            hist_births.append(births_total); hist_deaths.append(deaths_total)
            hist_dconf.append(deaths_conflict); hist_conflicts.append(conflicts_current)
            hist_eavg.append(e_avg); hist_aavg.append(a_avg)

        if stepped and ticks % redraw_every == 0:
            bg = food_surface(world.food)
            bg_scaled = pygame.transform.smoothscale(bg, (map_rect[2], map_rect[3]))

        screen.fill(WINDOW_BG)

        stats = {
            "Tick": (ticks, None),
            "Popolazione": (hist_pop[-1] if hist_pop else len(agents), list(hist_pop)),
            "Maschi": (hist_male[-1] if hist_male else 0, list(hist_male)),
            "Femmine": (hist_fem[-1] if hist_fem else 0, list(hist_fem)),
            "Infetti": (hist_infected[-1] if hist_infected else 0, list(hist_infected)),
            "Nati totali": (hist_births[-1] if hist_births else births_total, list(hist_births)),
            "Morti totali": (hist_deaths[-1] if hist_deaths else deaths_total, list(hist_deaths)),
            "Morti per conflitto": (hist_dconf[-1] if hist_dconf else deaths_conflict, list(hist_dconf)),
            "Conflitti (tick)": (hist_conflicts[-1] if hist_conflicts else conflicts_current, list(hist_conflicts)),
            "Energia media": (hist_eavg[-1] if hist_eavg else 0.0, list(hist_eavg)),
            "Età media (anni)": (hist_aavg[-1] if hist_aavg else 0.0, list(hist_aavg)),
        }
        from .panels import draw_stats_panel  # assicurati di avere import pygame in panels.py
        draw_stats_panel(surface=screen, rect=(0, 0, LEFT_PANEL_W, win_h),
                         title="Statistiche", stats=stats, font_name=FONT_NAME)

        mx, my, mw, mh = map_rect
        screen.blit(bg_scaled, (mx, my))
        draw_agents(screen, agents, cfg, mx, my, mw, mh)

        if cfg.show_conflict_flash:
            draw_conflict_flashes(screen, conflict_flashes, cfg, mx, my, mw, mh)

        legend_lines = make_legend_lines(cfg)
        draw_panel(screen, (win_w - RIGHT_PANEL_W, 0, RIGHT_PANEL_W, win_h),
                   "Legenda & Regole", legend_lines, font_name=FONT_NAME)

        if show_ctrl:
            ctrl.render(screen, (0, 0, win_w, win_h))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
