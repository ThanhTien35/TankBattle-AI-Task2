"""Regression tests for maps, logs, evaluation, and integration."""
import csv
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from tankbattle.agents.registry import ExternalAgent
from tankbattle.agents.search import SearchAgent, evaluate
from benchmarks.compare import run_benchmark
from benchmarks.scenarios import get_scenarios
from benchmarks.tournament import run_tournament
from tankbattle.engine.game import apply_action, legal_actions
from tankbattle.engine.maps import MAP_NAMES, get_map
from tankbattle.engine.model import Action, Base, Bullet, GameState, Tank, Wall, WIDTH, HEIGHT


class MapTests(unittest.TestCase):
    def test_three_independent_valid_maps(self):
        self.assertEqual(len(MAP_NAMES), 3)
        all_walls = []
        for name in MAP_NAMES:
            state = get_map(name)
            coords = [(t.x, t.y) for t in state.tanks]
            coords += [(b.x, b.y) for b in state.bases]
            coords += [(w.x, w.y) for w in state.walls]
            with self.subTest(map=name):
                self.assertEqual(len(coords), len(set(coords)))
                self.assertTrue(all(0 <= x < WIDTH and 0 <= y < HEIGHT for x, y in coords))
                self.assertEqual([t.hp for t in state.tanks], [6, 6])
                self.assertEqual([b.hp for b in state.bases], [9, 9])
                self.assertTrue(all(w.hp == 3 for w in state.walls))
            all_walls.append(tuple((w.x, w.y) for w in state.walls))
        self.assertEqual(len(set(all_walls)), 3)

    def test_all_six_actions_and_blocked_turn(self):
        state = GameState((Tank(1, 1, 1, 0), Tank(12, 12, -1, 0)),
                          (Base(0, 0), Base(14, 14)), (Wall(2, 1),))
        self.assertEqual(len(legal_actions(state)), 6)
        new_state = apply_action(state, Action.MOVE_RIGHT)
        self.assertEqual((new_state.tanks[0].x, new_state.tanks[0].y), (1, 1))
        self.assertEqual((new_state.tanks[0].dx, new_state.tanks[0].dy), (1, 0))


class HistoryTests(unittest.TestCase):
    def test_wall_hit_events_and_state_snapshots(self):
        state = GameState((Tank(2, 5, 1, 0), Tank(12, 5, -1, 0)),
                          (Base(1, 7), Base(13, 7)), (Wall(4, 5),))
        old = state
        events = []
        state = apply_action(state, Action.FIRE, events=events)
        self.assertEqual(old.walls[0].hp, 3)
        self.assertEqual(state.walls[0].hp, 2)
        self.assertTrue(any('wall' in e and '3->2' in e for e in events))
        self.assertTrue(any('fired' in e for e in events))

    def test_base_destroyed_logged(self):
        state = GameState((Tank(2, 5, 1, 0), Tank(12, 5, -1, 0)),
                          (Base(1, 7), Base(4, 5, 1)), ())
        events = []
        new = apply_action(state, Action.FIRE, events=events)
        self.assertEqual(new.winner, 0)
        self.assertEqual(new.bases[1].hp, 0)
        self.assertTrue(any('P2 Base: 1->0' in e for e in events))
        self.assertTrue(any('GAME OVER' in e for e in events))

    def test_heurstic_antisymmetric(self):
        for scenario in get_scenarios('all'):
            with self.subTest(scenario=scenario.name):
                state = scenario.state
                self.assertAlmostEqual(evaluate(state, 0, True), -evaluate(state, 1, True))

    def test_minimax_pruning_value_parity_on_maps(self):
        for scenario in get_scenarios('maps'):
            for a, b in (('Minimax', 'Alpha-Beta'),
                         ('Heuristic Minimax', 'Heuristic Alpha-Beta')):
                plain = SearchAgent(a, 3)
                prune = SearchAgent(b, 3)
                first = plain.choose_action(scenario.state)
                second = prune.choose_action(scenario.state)
                with self.subTest(map=scenario.name, mode=a):
                    self.assertEqual(plain.stats.score, prune.stats.score)
                    self.assertEqual(first, second)
                    self.assertLessEqual(prune.stats.nodes, plain.stats.nodes)

    def test_map_benchmark_and_tournament_exports(self):
        with tempfile.TemporaryDirectory() as folder:
            bench = Path(folder) / 'bench.csv'
            matches = Path(folder) / 'matches.csv'
            summary = Path(folder) / 'summary.csv'
            rows = run_benchmark(depth=2, repeats=1, suite='maps', output=str(bench))
            self.assertEqual(len(rows), 12)
            with bench.open(encoding='utf-8-sig') as f:
                self.assertEqual(len(list(csv.DictReader(f))), 12)
            games, sums = run_tournament(depth=1, rounds=1, max_plies=2,
                                         suite='maps', modes=['Minimax', 'Alpha-Beta'],
                                         output=str(matches), summary_output=str(summary))
            self.assertEqual(len(games), 6)
            self.assertEqual(len(sums), 2)
            self.assertTrue(matches.exists() and summary.exists())

    def test_external_agent_legal(self):
        agent = ExternalAgent('tankbattle.external_agents.example_agent')
        for scenario in get_scenarios('maps'):
            self.assertIn(agent.choose_action(scenario.state), legal_actions(scenario.state))


if __name__ == '__main__':
    unittest.main()
