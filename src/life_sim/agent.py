from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Agent:
    id: int
    x: int
    y: int
    energy: float = 10.0

    # età in anni (tutte le regole sono in anni; i tick aggiungono years_per_tick)
    age_years: float = 0.0
    max_age: float = 80.0

    speed: int = 1
    vision: int = 4
    sex: str = "M"  # "M" o "F"

    # Riproduzione
    repro_cooldown_years: float = 0.0

    # Malattia
    infected: bool = False
    disease_years: float = 0.0

    # Foraging/conflitto (tracking ultimi tick)
    ate_recent_ticks: int = 0         # >0 se ha mangiato in uno degli ultimi tick (decade nel tempo)
    hunger_streak_ticks: int = 0      # tick consecutivi senza mangiare

    # Visual/UI: evidenziazione rischio conflitto
    at_risk_conflict: bool = False
