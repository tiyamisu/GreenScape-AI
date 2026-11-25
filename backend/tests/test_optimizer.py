import unittest
from greenscape.city import make_city
from greenscape.abc import ABCConfig, ArtificialBeeColony
from greenscape.model import Candidate, Weights, evaluate, repair

class OptimizerTests(unittest.TestCase):
    def setUp(self): self.zones = make_city("mixed", 41)

    def test_city_is_reproducible_and_synthetic(self):
        self.assertEqual(self.zones, make_city("mixed", 41))
        self.assertEqual(400, len(self.zones))
        self.assertNotEqual(self.zones, make_city("commercial", 41))

    def test_repair_enforces_budget_suitability_and_ground_exclusivity(self):
        c = Candidate({(z.id, k) for z in self.zones[:20] for k in ("tree", "park", "roof")})
        repair(c, self.zones, 15000)
        self.assertLessEqual(c.cost, 15000)
        ground = [z for z,k in c.allocations if k != "roof"]
        self.assertEqual(len(ground), len(set(ground)))
        suitability = {z.id: z for z in self.zones}
        self.assertTrue(all((suitability[z].roof_suitability if k == "roof" else suitability[z].tree_suitability if k == "tree" else suitability[z].park_suitability) >= .25 for z,k in c.allocations))

    def test_objective_weight_validation(self):
        with self.assertRaises(ValueError): Weights(0, 0, 0, 0).normalized()
        with self.assertRaises(ValueError): Weights(-1, 1, 1, 1).normalized()

    def test_seeded_optimizer_is_reproducible_and_best_never_deteriorates(self):
        cfg = ABCConfig(food_sources=5, onlookers=5, iterations=12, abandonment_limit=3, seed=19, budget=60000)
        a = ArtificialBeeColony(self.zones, cfg); result_a = a.run()
        b = ArtificialBeeColony(self.zones, cfg); result_b = b.run()
        self.assertEqual(result_a.allocations, result_b.allocations)
        self.assertEqual(result_a.fitness, result_b.fitness)
        bests = [row["best_fitness"] for row in a.history]
        self.assertEqual(bests, sorted(bests))
        self.assertLessEqual(result_a.cost, cfg.budget)

    def test_algorithm_events_are_real_and_scout_can_run(self):
        events=[]
        engine=ArtificialBeeColony(self.zones, ABCConfig(3, 3, 8, 1, 4, 10000), emit=events.append)
        engine.run()
        kinds={e["type"] for e in events}
        self.assertIn("employed_bee_exploring", kinds)
        self.assertIn("onlooker_selected", kinds)
        self.assertIn("scout_activated", kinds)
        self.assertEqual(8, len(engine.history))

if __name__ == "__main__": unittest.main()
