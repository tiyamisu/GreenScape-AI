# API

- `GET /api/health` — service health.
- `GET /api/scenarios` — available synthetic scenario names.
- `GET /api/city/{scenario}?seed=41` — reproducible 20 × 20 synthetic grid.
- `POST /api/optimize` — run custom ABC synchronously and return the accepted best allocations, objective components, history, evaluations and actual algorithm events.
- `POST /api/runs` — start a background optimization job and return its run ID/status.
- `GET /api/runs/{run_id}` — read job status, iteration, best fitness, history and completed result.
- `POST /api/runs/{run_id}/pause|resume|step|stop` — cooperative controls at iteration boundaries; single-step is available while paused.
- `WS /api/runs/{run_id}/events` — stream actual ABC events and the final result.

Development CORS allows the Vite origins `localhost:5173` and `127.0.0.1:5173`.

The synchronous optimize and background-run requests accept scenario, seed, iterations, food_sources, onlookers, abandonment_limit, budget and objective weights. Limits and invalid weights are validated. The synchronous endpoint remains available for compatibility. In-memory background jobs are capped at 50 recent jobs.
