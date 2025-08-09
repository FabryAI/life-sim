from __future__ import annotations
from .config import SimConfig
from .world import World
from .agent import Agent
from .scheduler import step

def main() -> None:
    cfg = SimConfig()
    world = World.create(cfg)
    agents = [Agent(id=i, x=i % cfg.width, y=(i*7) % cfg.height) for i in range(cfg.initial_agents)]
    for t in range(100):  # breve demo headless
        agents = step(world, agents)
    print(f"Simulazione terminata: {len(agents)} agenti vivi dopo 100 tick.")

if __name__ == "__main__":
    main()
