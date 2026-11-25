"""GreenScape API with synchronous compatibility and controllable run jobs."""
import asyncio
from queue import Empty
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from .city import SCENARIOS, make_city
from .abc import ABCConfig, ArtificialBeeColony
from .model import Weights
from .jobs import JobRegistry, OptimizationJob, candidate_result

app = FastAPI(title="GreenScape AI", version="0.1.0", description="Synthetic urban greening optimization")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
                   allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

class RunRequest(BaseModel):
    scenario: str = "mixed"
    seed: int = 7
    iterations: int = Field(100, ge=1, le=2000)
    food_sources: int = Field(12, ge=2, le=100)
    onlookers: int = Field(12, ge=1, le=200)
    abandonment_limit: int = Field(20, ge=1, le=1000)
    budget: float = Field(250000, ge=0)
    weights: Weights = Field(default_factory=Weights)

@app.get("/api/health")
def health(): return {"status":"ok", "service":"greenscape-ai"}

@app.get("/api/scenarios")
def scenarios(): return [{"id": k, "name": v} for k,v in SCENARIOS.items()]

@app.get("/api/city/{scenario}")
def city(scenario: str, seed: int = 41):
    try: zones = make_city(scenario, seed)
    except ValueError as exc: raise HTTPException(404, str(exc)) from exc
    return {"synthetic":True, "grid_size":20, "scenario":scenario, "zones":[z.__dict__ for z in zones]}

@app.post("/api/optimize")
def optimize(req: RunRequest):
    try:
        zones = make_city(req.scenario)
        events = []
        engine = ArtificialBeeColony(zones, ABCConfig(req.food_sources, req.onlookers, req.iterations,
            req.abandonment_limit, req.seed, req.budget), req.weights, events.append)
        best = engine.run()
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc
    return {**candidate_result(engine), "events":events}

run_jobs = JobRegistry()

@app.post("/api/runs", status_code=202)
def start_run(req: RunRequest):
    try:
        config = ABCConfig(req.food_sources, req.onlookers, req.iterations, req.abandonment_limit, req.seed, req.budget)
        job = OptimizationJob(req.scenario, config, req.weights)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    run_jobs.add(job)
    job.start()
    return job.snapshot()

def find_job(run_id: str):
    job = run_jobs.get(run_id)
    if not job:
        raise HTTPException(404, "Run not found")
    return job

@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    return find_job(run_id).snapshot()

@app.post("/api/runs/{run_id}/pause")
def pause_run(run_id: str):
    job = find_job(run_id); job.pause(); return job.snapshot()

@app.post("/api/runs/{run_id}/resume")
def resume_run(run_id: str):
    job = find_job(run_id); job.resume(); return job.snapshot()

@app.post("/api/runs/{run_id}/step")
def step_run(run_id: str):
    job = find_job(run_id)
    try: job.step()
    except ValueError as exc: raise HTTPException(409, str(exc)) from exc
    return job.snapshot()

@app.post("/api/runs/{run_id}/stop")
def stop_run(run_id: str):
    job = find_job(run_id); job.stop(); return job.snapshot()

@app.websocket("/api/runs/{run_id}/events")
async def run_events(websocket: WebSocket, run_id: str):
    job = run_jobs.get(run_id)
    if not job:
        await websocket.close(code=4404, reason="Run not found")
        return
    await websocket.accept()
    channel, backlog = job.subscribe()
    try:
        for event in backlog:
            await websocket.send_json(event)
        while job.status not in ("completed", "stopped", "error") or not channel.empty():
            try:
                event = await asyncio.to_thread(channel.get, True, .25)
                await websocket.send_json(event)
            except Empty:
                continue
    except WebSocketDisconnect:
        pass
    finally:
        job.unsubscribe(channel)
