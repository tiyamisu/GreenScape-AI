"""Transparent weighted objective and repaired discrete city allocations."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal
from .city import Zone

Kind = Literal["tree", "park", "roof"]
COST = {"tree": 1200.0, "park": 24000.0, "roof": 9000.0}
CAPACITY = {"tree": .055, "park": .30, "roof": .20}

@dataclass
class Weights:
    heat: float = .35
    green: float = .25
    population: float = .30
    cost: float = .10
    def normalized(self) -> dict[str, float]:
        vals = {"heat": self.heat, "green": self.green, "population": self.population, "cost": self.cost}
        if any(v < 0 for v in vals.values()) or sum(vals.values()) <= 0:
            raise ValueError("Objective weights must be non-negative with a positive sum")
        total = sum(vals.values())
        return {k: v/total for k, v in vals.items()}

@dataclass
class Candidate:
    allocations: set[tuple[str, Kind]] = field(default_factory=set)
    fitness: float = float("-inf")
    components: dict[str, float] = field(default_factory=dict)
    cost: float = 0.0

    def clone(self) -> "Candidate":
        return Candidate(set(self.allocations), self.fitness, dict(self.components), self.cost)

def repair(candidate: Candidate, zones: list[Zone], budget: float) -> Candidate:
    by_id = {z.id: z for z in zones}
    valid = []
    for zid, kind in candidate.allocations:
        z = by_id.get(zid)
        suitability = {"tree": z.tree_suitability, "park": z.park_suitability, "roof": z.roof_suitability}.get(kind) if z else None
        if suitability is not None and suitability >= .25 and (kind == "roof" or z.open_land >= CAPACITY[kind]):
            valid.append((z.priority * suitability, z.id, kind))
    # A ground parcel hosts one intervention; rooftops may co-exist with it.
    valid.sort(reverse=True)
    accepted: set[tuple[str, Kind]] = set()
    ground: set[str] = set()
    spent = 0.0
    for _, zid, kind in valid:
        if (zid, kind) in accepted or (kind != "roof" and zid in ground):
            continue
        if spent + COST[kind] > max(0, budget):
            continue
        accepted.add((zid, kind)); spent += COST[kind]
        if kind != "roof": ground.add(zid)
    candidate.allocations = accepted
    candidate.cost = spent
    return candidate

def evaluate(candidate: Candidate, zones: list[Zone], budget: float, weights: Weights) -> Candidate:
    w = weights.normalized()
    by_id = {z.id: z for z in zones}
    heat = green = pop = 0.0
    total_pop = sum(z.population_density for z in zones) or 1.0
    for zid, kind in candidate.allocations:
        z = by_id[zid]
        if kind == "tree": cooling, cover = .45, .055
        elif kind == "park": cooling, cover = .8, .30
        else: cooling, cover = .30, .20
        impact = z.priority * (0.55 + z.temperature_c/45) * (1 - .35*z.building_density)
        heat += cooling * impact
        green += cover
        pop += cooling * z.population_density
    # Scales are fixed and documented so scores are comparable within a scenario family.
    h = min(1.0, heat / max(1, len(zones)*.012))
    g = min(1.0, green / max(1, len(zones)*.12))
    p = min(1.0, pop / max(1, total_pop*.08))
    c = candidate.cost / max(1.0, budget)
    candidate.components = {"heat": h, "green": g, "population": p, "cost": c}
    candidate.fitness = w["heat"]*h + w["green"]*g + w["population"]*p - w["cost"]*c
    return candidate
