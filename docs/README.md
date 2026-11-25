# GreenScape AI

Artificial Bee Colony-Based Intelligent Urban Green Space Optimization for Sustainable Smart Cities.

GreenScape AI is an educational urban greening simulator. Its current backend creates reproducible synthetic, Bengaluru-inspired 20 × 20 city scenarios and applies a custom discrete Artificial Bee Colony optimizer to tree, park and green-roof allocations under budget and suitability constraints. Synthetic temperatures and all impacts are illustrative; they are not measured Bengaluru data or calibrated forecasts.

## Current implementation

- Five seeded city scenarios with structured zone attributes.
- Custom employed, onlooker and scout phases; greedy selection and fitness-based probabilistic source selection.
- Normalized weighted fitness, deterministic feasibility repair, event stream, history and global best tracking.
- FastAPI scenario, city, health and synchronous optimization endpoints.
- Background ABC jobs with pause, resume, cooperative stop, single-step and actual WebSocket progress events. The synchronous endpoint remains supported.
- Focused checks for scenario reproducibility, constraints, weight validation, deterministic optimization, event types and monotone best-so-far.

## Run the backend

Python 3.10+ with FastAPI, Pydantic and Uvicorn is required. Install the backend dependencies with `python -m pip install -r backend/requirements.txt` (the current model does not require NumPy directly).

```powershell
$env:PYTHONPATH = "backend"
python -m uvicorn greenscape.api:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API reference.

## Run the frontend

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The API must be running for the city data and optimization controls.

## Checks

```powershell
$env:PYTHONPATH = "backend"
python -m unittest discover -s backend/tests
```

## Interface

The React/TypeScript frontend provides eight routed workspaces, an interactive Three.js city, scenario and layer controls, live ABC optimization, analytics, algorithm education, browser-local saved runs, exports and settings. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for verified coverage and remaining work.

## Model and implementation notes

- [Architecture](ARCHITECTURE.md)
- [ABC implementation](ALGORITHM_EXPLANATION.md)
- [Mathematical model](MATHEMATICAL_MODEL.md)
- [API](API_DOCUMENTATION.md)

## Screenshots

To be added after the frontend is implemented.
