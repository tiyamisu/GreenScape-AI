"""Discrete Artificial Bee Colony optimizer with emitted algorithm events."""
from __future__ import annotations
from dataclasses import dataclass
import random
from typing import Callable
from .city import Zone
from .model import Candidate, Kind, Weights, evaluate, repair

Event = Callable[[dict], None]

@dataclass
class ABCConfig:
    food_sources: int = 12
    onlookers: int = 12
    iterations: int = 100
    abandonment_limit: int = 20
    seed: int = 7
    budget: float = 250_000

class ArtificialBeeColony:
    """Binary set of (zone, infrastructure) decisions; repaired before scoring."""
    kinds: tuple[Kind, ...] = ("tree", "park", "roof")
    def __init__(self, zones: list[Zone], config: ABCConfig, weights: Weights | None = None, emit: Event | None = None):
        if config.food_sources < 2 or config.iterations < 1 or config.onlookers < 1 or config.abandonment_limit < 1 or config.budget < 0:
            raise ValueError("Invalid ABC configuration")
        self.zones, self.config, self.weights = zones, config, weights or Weights()
        self.emit = emit or (lambda event: None)
        self.rng = random.Random(config.seed)
        self.evaluations = 0
        self.trials = [0] * config.food_sources
        self.population = [self._random_candidate() for _ in range(config.food_sources)]
        self.best = max((c.clone() for c in self.population), key=lambda c: c.fitness)
        self.history: list[dict] = []

    def _score(self, c: Candidate) -> Candidate:
        repair(c, self.zones, self.config.budget)
        evaluate(c, self.zones, self.config.budget, self.weights)
        self.evaluations += 1
        return c

    def _random_candidate(self) -> Candidate:
        c = Candidate({(z.id, k) for z in self.zones for k in self.kinds if self.rng.random() < .035})
        return self._score(c)

    def _neighbor(self, source: Candidate) -> Candidate:
        c = source.clone()
        z = self.rng.choice(self.zones); k = self.rng.choice(self.kinds); item = (z.id, k)
        if item in c.allocations:
            c.allocations.remove(item)
        else:
            # A discrete add/replace move; repair handles parcel and budget constraints.
            if k != "roof": c.allocations = {a for a in c.allocations if a[0] != z.id or a[1] == "roof"}
            c.allocations.add(item)
        return self._score(c)

    @staticmethod
    def _probabilities(population: list[Candidate]) -> list[float]:
        low = min(c.fitness for c in population)
        shifted = [c.fitness-low+1e-12 for c in population]
        total = sum(shifted)
        return [v/total for v in shifted] if total else [1/len(population)]*len(population)

    def step(self) -> dict:
        self.emit({"type":"iteration_started", "iteration":len(self.history)+1})
        improvements = scouts = 0
        for i, source in enumerate(self.population):
            self.emit({"type":"employed_bee_exploring", "source":i})
            trial = self._neighbor(source)
            if trial.fitness > source.fitness:
                self.population[i] = trial; self.trials[i] = 0; improvements += 1
                self.emit({"type":"candidate_improved", "source":i, "fitness":trial.fitness})
            else: self.trials[i] += 1
        probs = self._probabilities(self.population)
        for bee in range(self.config.onlookers):
            idx = self.rng.choices(range(len(probs)), weights=probs, k=1)[0]
            self.emit({"type":"onlooker_selected", "source":idx, "bee":bee, "probability":probs[idx]})
            trial = self._neighbor(self.population[idx])
            if trial.fitness > self.population[idx].fitness:
                self.population[idx] = trial; self.trials[idx] = 0; improvements += 1
                self.emit({"type":"candidate_improved", "source":idx, "fitness":trial.fitness})
            else: self.trials[idx] += 1
        for i, count in enumerate(self.trials):
            if count >= self.config.abandonment_limit:
                self.emit({"type":"food_source_abandoned", "source":i})
                self.emit({"type":"scout_activated", "source":i})
                self.population[i] = self._random_candidate(); self.trials[i] = 0; scouts += 1
        generation_best = max(self.population, key=lambda c:c.fitness)
        if generation_best.fitness > self.best.fitness:
            self.best = generation_best.clone()
            self.emit({"type":"global_best_updated", "iteration":len(self.history)+1, "fitness":self.best.fitness, "allocations":[list(a) for a in sorted(self.best.allocations)]})
        row = {"iteration":len(self.history)+1, "best_fitness":self.best.fitness,
               "average_fitness":sum(c.fitness for c in self.population)/len(self.population),
               "improvements":improvements, "scouts":scouts, "evaluations":self.evaluations}
        self.history.append(row); self.emit({"type":"iteration_completed", **row})
        return row

    def run(self, iterations: int | None = None) -> Candidate:
        self.emit({"type":"optimization_started", "seed":self.config.seed})
        for _ in range(iterations if iterations is not None else self.config.iterations): self.step()
        self.emit({"type":"optimization_completed", "fitness":self.best.fitness, "evaluations":self.evaluations})
        return self.best.clone()
