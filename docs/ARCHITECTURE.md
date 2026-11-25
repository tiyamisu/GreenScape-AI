# Architecture

GreenScape AI separates optimization from presentation. The Python service owns the synthetic city data, feasibility rules, objective evaluation, ABC lifecycle, analytics and saved runs. A run emits structured algorithm events; API consumers use those same events to render bees and update the city. The React client owns navigation and rendering only, and must not invent candidate solutions or environmental results.

The first transport is REST for scenario/configuration and run control, with a WebSocket for progress events. Optimization work runs in a background worker so API handlers remain responsive. Scenario inputs are deterministic and explicitly synthetic. Lightweight local persistence is planned for completed runs.

The initial candidate is a set of typed zone allocations (trees, parks and green roofs). Feasibility repair removes unsuitable or over-budget allocations deterministically. Fitness is a weighted sum of normalized cooling, green coverage and population benefit minus normalized cost. Assumptions and units are exposed in the model documentation.

## Roadmap

1. Backend data and optimizer.
2. FastAPI controls and event stream.
3. React dashboard and interactive 3D city.
4. Analytics, scenarios, benchmarking and exports.
