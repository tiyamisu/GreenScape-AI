# ABC Algorithm

Each food source is a set of binary decisions `(zone_id, infrastructure_kind)` for tree, park and green roof. The representation is discrete; no continuous ABC equation is applied to grid indices. A deterministic feasibility repair checks land suitability, enforces at most one ground intervention per parcel, and removes allocations in low-priority order until the budget is respected.

The employed phase makes one discrete add/remove move for each food source and applies greedy selection. Onlookers sample sources with probability proportional to shifted positive fitness and use the same neighbourhood and greedy rule. A source reaching the abandonment limit is replaced by a randomized repaired source (scout phase). A separate best-so-far copy guarantees the reported global best cannot deteriorate. The local seeded PRNG makes runs reproducible.

The event callback is called by those operations and is intended to drive UI animation. The optimizer itself has no dependency on React or Three.js. Current service execution is synchronous; background lifecycle controls and WebSocket transport are planned next.
