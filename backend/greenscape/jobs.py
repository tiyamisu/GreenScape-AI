"""Threaded optimizer jobs with cooperative pause, stop, step and event delivery."""
from __future__ import annotations

from queue import Empty, Queue
import threading
import uuid
from .abc import ABCConfig, ArtificialBeeColony
from .city import make_city
from .model import Weights


def candidate_result(engine: ArtificialBeeColony) -> dict:
    best = engine.best
    return {"synthetic": True, "fitness": best.fitness, "components": best.components,
            "cost": best.cost, "allocations": [{"zone_id": z, "kind": k} for z, k in sorted(best.allocations)],
            "history": engine.history, "evaluations": engine.evaluations}


class OptimizationJob:
    def __init__(self, scenario: str, config: ABCConfig, weights: Weights):
        self.id = str(uuid.uuid4())
        self.scenario = scenario
        self.config = config
        self.condition = threading.Condition()
        self.status = "running"
        self.stop_requested = False
        self.step_tokens = 0
        self.events: list[dict] = []
        self.listeners: list[Queue] = []
        self.lock = threading.Lock()
        self.error: str | None = None
        self.engine = ArtificialBeeColony(make_city(scenario), config, weights, self.emit)
        self.thread = threading.Thread(target=self.work, name=f"abc-{self.id[:8]}", daemon=True)

    def emit(self, event: dict) -> None:
        with self.lock:
            self.events.append(event)
            listeners = tuple(self.listeners)
        for listener in listeners:
            listener.put(event)

    def work(self) -> None:
        try:
            self.emit({"type": "optimization_started", "run_id": self.id, "seed": self.config.seed})
            self.emit({"type": "global_best_updated", "iteration": 0, "fitness": self.engine.best.fitness,
                       "allocations": [list(a) for a in sorted(self.engine.best.allocations)]})
            while len(self.engine.history) < self.config.iterations:
                with self.condition:
                    self.condition.wait_for(lambda: not (self.status == "paused" and self.step_tokens == 0) or self.stop_requested)
                    if self.stop_requested:
                        self.status = "stopped"
                        self.emit({"type": "optimization_stopped", "iteration": len(self.engine.history)})
                        return
                    if self.status == "paused" and self.step_tokens:
                        self.step_tokens -= 1
                self.engine.step()
                with self.condition:
                    if self.status != "paused":
                        self.status = "running"
            self.status = "completed"
            result = candidate_result(self.engine)
            self.emit({"type": "optimization_completed", "fitness": self.engine.best.fitness,
                       "evaluations": self.engine.evaluations, "result": result})
        except Exception as exc:  # surfaced through status endpoint and event stream
            self.error = str(exc)
            self.status = "error"
            self.emit({"type": "optimization_error", "message": self.error})

    def start(self) -> None:
        self.thread.start()

    def pause(self) -> None:
        with self.condition:
            if self.status == "running":
                self.status = "paused"

    def resume(self) -> None:
        with self.condition:
            if self.status == "paused":
                self.status = "running"
                self.condition.notify_all()

    def step(self) -> None:
        with self.condition:
            if self.status != "paused":
                raise ValueError("Single-step is available only while paused")
            self.step_tokens += 1
            self.condition.notify_all()

    def stop(self) -> None:
        with self.condition:
            if self.status not in ("completed", "stopped", "error"):
                self.stop_requested = True
                self.condition.notify_all()

    def snapshot(self) -> dict:
        return {"run_id": self.id, "scenario": self.scenario, "status": self.status,
                "iteration": len(self.engine.history), "iterations": self.config.iterations,
                "best_fitness": self.engine.best.fitness, "history": list(self.engine.history),
                "result": candidate_result(self.engine) if self.status == "completed" else None,
                "error": self.error}

    def subscribe(self) -> tuple[Queue, list[dict]]:
        q: Queue = Queue()
        with self.lock:
            backlog = list(self.events)
            self.listeners.append(q)
        return q, backlog

    def unsubscribe(self, q: Queue) -> None:
        with self.lock:
            if q in self.listeners:
                self.listeners.remove(q)


class JobRegistry:
    def __init__(self):
        self._jobs: dict[str, OptimizationJob] = {}
        self._lock = threading.Lock()

    def add(self, job: OptimizationJob) -> None:
        with self._lock:
            terminal = [key for key, value in self._jobs.items() if value.status in ("completed", "stopped", "error")]
            while len(self._jobs) >= 50 and terminal:
                self._jobs.pop(terminal.pop(0), None)
            self._jobs[job.id] = job

    def get(self, job_id: str) -> OptimizationJob | None:
        with self._lock:
            return self._jobs.get(job_id)


jobs = JobRegistry()

