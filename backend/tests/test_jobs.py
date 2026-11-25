import time
import unittest
from fastapi.testclient import TestClient
from greenscape.api import app

class JobApiTests(unittest.TestCase):
    def setUp(self): self.client = TestClient(app)

    def test_pause_single_step_resume_and_stop(self):
        started = self.client.post('/api/runs', json={"iterations": 1500, "seed": 101})
        self.assertEqual(202, started.status_code)
        run_id = started.json()['run_id']
        self.client.post(f'/api/runs/{run_id}/pause')
        time.sleep(.03)
        before = self.client.get(f'/api/runs/{run_id}').json()['iteration']
        paused = self.client.get(f'/api/runs/{run_id}').json()
        self.assertEqual('paused', paused['status'])
        self.client.post(f'/api/runs/{run_id}/step')
        deadline = time.time() + 2
        while time.time() < deadline:
            current = self.client.get(f'/api/runs/{run_id}').json()
            if current['iteration'] > before: break
            time.sleep(.01)
        self.assertEqual(before + 1, current['iteration'])
        time.sleep(.03)
        self.assertEqual('paused', self.client.get(f'/api/runs/{run_id}').json()['status'])
        self.client.post(f'/api/runs/{run_id}/resume')
        self.client.post(f'/api/runs/{run_id}/stop')
        deadline = time.time() + 2
        while time.time() < deadline and self.client.get(f'/api/runs/{run_id}').json()['status'] not in ('stopped', 'completed'):
            time.sleep(.01)
        self.assertEqual('stopped', self.client.get(f'/api/runs/{run_id}').json()['status'])

    def test_websocket_streams_actual_algorithm_events(self):
        start = self.client.post('/api/runs', json={"iterations": 2, "food_sources": 3, "onlookers": 3, "seed": 32}).json()
        with self.client.websocket_connect(f"/api/runs/{start['run_id']}/events") as ws:
            kinds=[]
            best_iterations=[]
            for _ in range(100):
                event=ws.receive_json(); kinds.append(event['type'])
                if event['type']=='global_best_updated': best_iterations.append(event['iteration'])
                if event['type']=='optimization_completed': break
        self.assertIn('employed_bee_exploring', kinds)
        self.assertIn('onlooker_selected', kinds)
        self.assertTrue(best_iterations)
        self.assertEqual(0, best_iterations[0])
        self.assertIn('optimization_completed', kinds)

if __name__ == '__main__': unittest.main()
