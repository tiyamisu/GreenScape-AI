# Mathematical model

For a configuration `x`, the initial score is `F(x) = wh H(x) + wg G(x) + wp P(x) - wc C(x)`. User weights must be nonnegative and have positive sum; they are normalized to sum to one. Components are bounded/normalized against fixed scenario-size scales. Infrastructure costs are illustrative synthetic assumptions: tree 1,200, park 24,000, green roof 9,000 budget units.

For each allocation, heat benefit uses a type-specific cooling coefficient multiplied by zone environmental priority, a temperature factor, and a building-density adjustment. Green benefit sums illustrative coverage fractions (tree .055, park .30, roof .20). Population benefit weights type cooling by normalized synthetic population density. Cost is total installed cost divided by budget. A zero budget permits only the empty solution; cost component uses a safe denominator. Fitness represents a comparative educational objective, not a calibrated temperature prediction.

Ground parcels can receive at most one of tree or park; rooftops can coexist with ground allocation. Tree and park suitability and open-land capacity are checked. Roof suitability is checked separately. A deterministic priority-ordered repair enforces budget and legality before evaluation, so infeasible allocations are never scored as if valid.

All city temperatures, land attributes, population values and resulting impacts are reproducible synthetic data. No metric represents observed Bengaluru conditions or a validated climate prediction.
