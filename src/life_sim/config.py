from dataclasses import dataclass

@dataclass(frozen=True)
class SimConfig:
    # Mondo / base
    seed: int = 42
    width: int = 128
    height: int = 128
    toroidal: bool = True

    # Popolazione iniziale
    initial_agents: int = 800
    initial_age_median_years: float = 25.0
    initial_age_spread_years: float = 8.0
    initial_infected_pct: float = 0.02

    # Tempo e tick
    tick_rate_hz: int = 15
    time_unit: str = "month"  # "year" | "month" | "day"

    # Risorse
    resource_regen_rate: float = 0.001
    initial_food_mean: float = 0.00001
    initial_food_flat: bool = False

    # Foraging
    min_eat_to_count: float = 0.02  # quantità minima per "ha mangiato" (per conflitti)

    # Riproduzione
    maturity_age_years: float = 16.0
    reproduction_energy_min: float = 15.0
    reproduction_cost: float = 5.0
    reproduction_cooldown_years: float = 1.0
    child_energy: float = 10.0
    reproduction_prob_per_meeting: float = 0.5

    # Malattia
    infection_annual_prob: float = 0.0005
    disease_energy_loss_per_year: float = 2.0
    disease_mortality_after_years: float = 5.0
    disease_mortality_annual_prob: float = 0.2
    disease_recovery_after_years: float = 2.0
    disease_recovery_annual_prob: float = 0.1

    # Backend (placeholder per GPU)
    compute_backend: str = "cpu"  # "cpu" | "cupy"

    # Conflitto
    conflict_hunger_ticks: int = 5
    conflict_kill_prob: float = 0.30                 # affamato vs chi mangia
    conflict_kill_prob_hungry_pair: float = 0.12     # affamato vs affamato
    conflict_bonus_if_weak: float = 0.10
    conflict_weak_energy_thresh: float = 5.0
    conflict_bonus_if_strong: float = 0.10
    conflict_strong_energy_thresh: float = 20.0

    # Visual conflitti (flash cerchio)
    show_conflict_flash: bool = True
    conflict_flash_duration_s: float = 1.0


def years_per_tick(cfg: SimConfig) -> float:
    return {
        "year": 1.0,
        "month": 1.0 / 12.0,
        "day": 1.0 / 365.0
    }.get(cfg.time_unit, 1.0 / 12.0)
