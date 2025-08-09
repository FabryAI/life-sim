from __future__ import annotations
import pygame
from typing import List, Sequence

PANEL_BG = (24, 24, 28)
PANEL_BORDER = (60, 60, 70)
TEXT_COLOR = (210, 210, 220)
TITLE_COLOR = (230, 230, 240)
GRID_COLOR = (80, 80, 90)
LINE_COLOR = (180, 220, 255)

def draw_panel(surface: pygame.Surface, rect, title: str, lines: List[str],
               font_name: str | None = None) -> None:
    x, y, w, h = rect
    pygame.draw.rect(surface, PANEL_BG, rect)
    pygame.draw.rect(surface, PANEL_BORDER, rect, 1)
    font_title = pygame.font.SysFont(font_name, 20, bold=True)
    font_line = pygame.font.SysFont(font_name, 18)
    surface.blit(font_title.render(title, True, TITLE_COLOR), (x+10, y+10))
    yy = y + 40
    for line in lines:
        if line == "---":
            pygame.draw.line(surface, GRID_COLOR, (x+10, yy+4), (x+w-10, yy+4), 1)
            yy += 12
            continue
        txt = font_line.render(line, True, TEXT_COLOR)
        surface.blit(txt, (x+10, yy))
        yy += 22

def _sparkline(surface: pygame.Surface, rect, data: Sequence[float]) -> None:
    x, y, w, h = rect
    pygame.draw.rect(surface, (20,20,24), rect)
    pygame.draw.rect(surface, GRID_COLOR, rect, 1)
    if not data or len(data) < 2:
        return
    dmin = min(data)
    dmax = max(data)
    rng = (dmax - dmin) if dmax != dmin else 1.0
    n = len(data)
    step = max(1, w // max(1, n-1))
    points = []
    for i, v in enumerate(data[-(w//step + 1):]):
        px = x + i * step
        py = y + h - int((v - dmin) / rng * (h-2)) - 1
        points.append((px, py))
    if len(points) >= 2:
        pygame.draw.lines(surface, LINE_COLOR, False, points, 2)

def draw_stats_panel(surface: pygame.Surface, rect, title: str,
                     stats: dict[str, tuple[float, list[float] | None]],
                     font_name: str | None = None) -> None:
    """
    stats: dict { label: (value, history or None) }
    Layout per voce:
      [Label.........................] [sparkline]
      [Valore allineato a sinistra..] [sparkline]
    """
    x, y, w, h = rect
    pygame.draw.rect(surface, PANEL_BG, rect)
    pygame.draw.rect(surface, PANEL_BORDER, rect, 1)

    font_title = pygame.font.SysFont(font_name, 20, bold=True)
    font_label = pygame.font.SysFont(font_name, 18, bold=False)
    font_value = pygame.font.SysFont(font_name, 18, bold=True)

    surface.blit(font_title.render(title, True, TITLE_COLOR), (x+10, y+10))

    yy = y + 44
    row_h = 36                 # più alto: 2 righe
    chart_w = int(w * 0.42)    # spazio sparkline a destra
    text_w = w - 20 - chart_w - 10

    for label, (val, hist) in stats.items():
        # Testo a sinistra (2 righe)
        label_surf = font_label.render(str(label), True, TEXT_COLOR)
        if isinstance(val, float) and not str(label).startswith("Tick"):
            val_text = f"{val:.2f}"
        else:
            val_text = f"{val}"
        value_surf = font_value.render(val_text, True, TEXT_COLOR)

        surface.blit(label_surf, (x+10, yy))             # riga 1: label
        surface.blit(value_surf, (x+10, yy + 18))         # riga 2: valore

        # Sparkline a destra (occupazione verticale = row_h - 6)
        if hist is not None and chart_w > 40:
            cx = x + 10 + text_w + 10
            cy = yy + 3
            ch = row_h - 6
            _sparkline(surface, (cx, cy, chart_w, ch), hist)

        yy += row_h

def make_legend_lines(cfg) -> list[str]:
    return [
        "Colori:",
        "Cibo: scala di grigi",
        "Maschio: ciano (schiarisce da giovane)",
        "Femmina: magenta (schiarisce da giovane)",
        "Rischio conflitto: bordo arancio",
        "---",
        "Regole (v3):",
        f"• Tempo: 1 tick = {cfg.time_unit}",
        "• Cibo rigenera verso 1, mappa toroidale",
        "• Movimento casuale (±1)",
        "• Foraging: mangia ≤0.1/cella (energia += 5×eat)",
        "• Manutenzione ~0.3 energia/anno; età in anni",
        "• Riproduzione:",
        f"  - Età ≥ {cfg.maturity_age_years} anni",
        f"  - Energia ≥ {cfg.reproduction_energy_min}, costo {cfg.reproduction_cost}",
        f"  - Cooldown {cfg.reproduction_cooldown_years} anni, p_incontro {int(cfg.reproduction_prob_per_meeting*100)}%",
        "• Malattia:",
        f"  - Inf. annua ≈ {cfg.infection_annual_prob*100:.2f}%, ΔE ~{cfg.disease_energy_loss_per_year}/anno",
        f"  - Mortalità dopo {cfg.disease_mortality_after_years} anni, p_annua ~{int(cfg.disease_mortality_annual_prob*100)}%",
        f"  - Guarigione dopo {cfg.disease_recovery_after_years} anni, p_annua ~{int(cfg.disease_recovery_annual_prob*100)}%",
        "• Conflitto:",
        f"  - Se {cfg.conflict_hunger_ticks} tick senza cibo",
        "    e vicino in certe condizioni:",
        f"    • vs chi sta mangiando → p≈{int(cfg.conflict_kill_prob*100)}%",
        f"    • vs affamato→ p≈{int(cfg.conflict_kill_prob_hungry_pair*100)}%",
        "  - Bonus: + debole/forte",
        "Controlli:",
        "SPACE: Pausa/Play   + / - : Velocità",
        "C: Pannello parametri   ESC: Esci",
        "Resize finestra: auto-adattamento",
    ]
