# GreenScape AI — Project Status

## Architecture

- `backend/`: synthetic city data, fitness model, custom ABC, FastAPI REST/WebSocket API and in-memory run jobs.
- `frontend/`: React/TypeScript/Vite, Three.js city, eight hash-routed views, analytics and browser-local reports.
- Optimization remains UI-independent; the client consumes backend results and actual ABC events.

## Completed

- Five reproducible synthetic 20 × 20 scenarios with explicit suitability and budget repair.
- Custom discrete ABC implementation with employed, onlooker and scout phases; synchronous endpoint preserved.
- Background run jobs with cooperative pause/resume/stop, single-step and actual WebSocket event delivery.
- Eight distinct views, warm nature palette, inline SVG city/leaf logo, accessible responsive navigation, warm/dark theme and browser-history routing.
- City Explorer includes four procedural building silhouettes with facade details, a coherent road grid with crossings and streetlights, landscaped parks, ponds, benches, varied vegetation, and optimized roof gardens. City elements and parcels can be selected for compact inspection; camera presets and focus controls are available.
- City Explorer supports orbit/zoom/reset, parcel details, building/road/vegetation layers and temperature/population/priority/building-density maps. Current-best snapshots from actual ABC best-improvement events can be replayed against baseline and final solutions for new runs.
- Final readability pass adds a shared responsive type scale across navigation, page headings, controls, metrics, reports, tooltips and inspector content without changing the established layout or palette.
- City rendering skips unchanged parcel components during unrelated application updates, reuses cached deterministic scenario datasets when revisiting them, and adaptively lowers pixel density during active camera movement. Contact shadow depth/blur passes now render once per scenario at 256px instead of repeating at the 512px default every frame; directional shadows and scene detail remain enabled. Growth animations stop updating after they finish.
- Optimization Lab sends weights, seed, budget, scenario, iterations, food-source/onlooker counts and abandonment limit; live updates are throttled to keep the map responsive.
- Scenario Studio, environmental analytics, algorithm explanation, local saved run archive, JSON/CSV exports and settings.

## Verification

- Backend: `PYTHONPATH=backend python -m unittest discover -s backend/tests` — 7 passed on 2026-11-25.
- Frontend: `cd frontend; npm run build` — passed on 2026-11-25 after the city-scene update. Three.js vendor is about 718 kB minified / 189 kB gzip (Vite reports the expected large-chunk warning).
- Final typography/performance pass: `cd frontend; npm run build` — passed. Browser checks rendered Mixed-use, Commercial core, Residential neighbourhood and Heat-stressed zone; the temperature legend remained present after switching to the heat layer. Exact FPS/frame-time profiling was unavailable in this browser preview, so no numeric performance gain is claimed.
- API and browser: health/city/optimization smoke checks, CORS from a second local dev port, all eight navigation views, direct route reload, real ABC runs and live event rendering verified. A browser run reached 100/100 with its result chart; a 500-cycle job record reached 500/500.
- ABC pause/resume/step/stop covered by backend job tests. Building selection and parcel metadata were verified in the browser after the visual update; a slow interactive browser check for pause and single-step remains outstanding.
- Background job history is in memory and capped at 50; completed report data is stored in browser local storage.

## Remaining

- Temperature layer currently shows initial synthetic estimates; implement a documented before/after cooling model before presenting temperature reduction.
- Add algorithm benchmark comparison and chart image export.
- Add automated frontend interaction tests and verify pause/single-step controls in a slow browser run.
- Optional: add durable backend run persistence.

## Commands

- Backend (PowerShell): `$env:PYTHONPATH="backend"; python -m uvicorn greenscape.api:app --reload`
- Backend checks (PowerShell): `$env:PYTHONPATH="backend"; python -m unittest discover -s backend/tests`
- Frontend: `cd frontend; npm run dev`
