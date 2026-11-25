"""Reproducible synthetic urban scenarios; values are illustrative, not measured."""
from __future__ import annotations

from dataclasses import dataclass
import math

GRID_SIZE = 20
SCENARIOS = {
    "commercial": "High-density commercial district",
    "residential": "Residential neighbourhood",
    "mixed": "Mixed-use urban district",
    "heat_stressed": "Heat-stressed urban zone",
    "outskirts": "Urban outskirts with available land",
}


@dataclass(frozen=True)
class Zone:
    id: str
    x: int
    y: int
    land_use: str
    building_density: float
    road_coverage: float
    existing_green: float
    population_density: float
    temperature_c: float
    open_land: float
    roof_suitability: float
    tree_suitability: float
    park_suitability: float
    priority: float


def make_city(scenario: str = "mixed", seed: int = 41) -> list[Zone]:
    """Create a deterministic 20x20 fictional Bengaluru-inspired city."""
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    # Small local PRNG avoids global random state and external dependencies.
    state = seed & 0xFFFFFFFF
    def rand() -> float:
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return state / 0x100000000

    zones = []
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            center = max(0.0, 1 - math.hypot(x - 9.5, y - 9.5) / 14)
            noise = (rand() - 0.5) * 0.18
            if scenario == "commercial":
                density, population, green, heat = .68 + .22*center, .58 + .35*center, .08, 3.0
            elif scenario == "residential":
                density, population, green, heat = .42 + .12*center, .50 + .18*center, .24, 1.0
            elif scenario == "heat_stressed":
                density, population, green, heat = .60 + .22*center, .62 + .26*center, .04, 5.0
            elif scenario == "outskirts":
                density, population, green, heat = .24 - .08*center, .24 + .1*center, .30, -.2
            else:
                density, population, green, heat = .42 + .30*center, .42 + .3*center, .15, 1.8
            density = min(.96, max(.08, density + noise))
            population = min(1.0, max(.1, population + noise))
            existing = min(.55, max(.01, green + (rand()-.5)*.10))
            roads = min(.38, max(.08, .17 + density*.12 + (rand()-.5)*.05))
            open_land = min(.8, max(.02, 1 - density - roads - existing*.3))
            temp = 29 + heat + density*4.1 - existing*3 + (rand()-.5)*1.8
            use = "commercial" if density > .68 else "residential" if population > .5 else "open"
            zones.append(Zone(
                id=f"Z-{y:02d}-{x:02d}", x=x, y=y, land_use=use,
                building_density=round(density, 4), road_coverage=round(roads, 4),
                existing_green=round(existing, 4), population_density=round(population, 4),
                temperature_c=round(temp, 2), open_land=round(open_land, 4),
                roof_suitability=round(min(1, density*.8 + rand()*.2), 4),
                tree_suitability=round(min(1, open_land*1.5 + .12), 4),
                park_suitability=round(min(1, open_land*1.3), 4),
                priority=round(min(1, max(0, (temp-28)/12*.55 + population*.45)), 4),
            ))
    return zones
