"""Tactical correctness and benchmark reproducibility tests (no pygame needed)."""
import tempfile
import unittest
from pathlib import Path
from tankbattle.agents.search import MODES, SearchAgent
from benchmarks.scenarios import get_scenarios, tournament_scenarios
from benchmarks.compare import run_benchmark
from benchmarks.tournament import run_tournament
from tankbattle.engine.model import Action, HEIGHT, WIDTH
from tankbattle.engine.game import apply_action, legal_actions


class ScenarioTests(unittest.TestCase):
    def test_scenarios_valid_positions(self):
        for s in get_scenarios('all') + tournament_scenarios():
            state = s.state
            occupied = [(t.x, t.y) for t in state.tanks]
            occupied += [(b.x, b.y) for b in state.bases]
            occupied += [(w.x, w.y) for w in state.walls]
            with self.subTest(scenario=s.name):
                self.assertEqual(len(occupied), len(set(occupied)))
                self.assertTrue(all(0 <= x < WIDTH and 0 <= y < HEIGHT
                                    for x, y in occupied))
                self.assertTrue(legal_actions(state))

    def test_imminent_bullet_forces_dodge(self):
        state = next(s.state for s in get_scenarios('tactical')
                     if s.name == 'Incoming bullet')
        for mode in MODES:
            with self.subTest(mode=mode):
                action = SearchAgent(mode, 3).choose_action(state)
                self.assertIn(action, (Action.MOVE_UP, Action.MOVE_DOWN))
                self.assertIsNone(apply_action(state, action).winner)
                self.assertEqual(apply_action(state, Action.FIRE).winner, 1)

    def test_forced_flank_is_not_fire(self):
        state = next(s.state for s in get_scenarios('tactical')
                     if s.name == 'Forced flank')
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assertEqual(SearchAgent(mode, 3).choose_action(state),
                                 Action.MOVE_RIGHT)

    def test_immediate_win_is_fire(self):
        state = next(s.state for s in get_scenarios('tactical')
                     if s.name == 'Finishing shot')
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assertEqual(SearchAgent(mode, 3).choose_action(state),
                                 Action.FIRE)
                self.assertEqual(apply_action(state, Action.FIRE).winner, 0)

    def test_alpha_beta_matches_minimax_with_same_evaluator(self):
        for scenario in get_scenarios('all'):
            for depth in (2, 3):
                for plain, pruning in (('Minimax', 'Alpha-Beta'),
                                       ('Heuristic Minimax', 'Heuristic Alpha-Beta')):
                    with self.subTest(scenario=scenario.name, depth=depth, mode=plain):
                        a, b = SearchAgent(plain, depth), SearchAgent(pruning, depth)
                        act_a = a.choose_action(scenario.state)
                        act_b = b.choose_action(scenario.state)
                        self.assertEqual(a.stats.score, b.stats.score)
                        self.assertEqual(act_a, act_b)
                        self.assertLessEqual(b.stats.nodes, a.stats.nodes)

    def test_csv_generation_and_mirrored_tournament(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = run_benchmark(depth=2, repeats=1, suite='tactical',
                                 output=str(Path(tmp) / 'benchmark.csv'))
            self.assertEqual(len(rows), 4 * len(MODES))
            self.assertTrue((Path(tmp) / 'benchmark.csv').exists())
            matches, summary = run_tournament(
                depth=1, max_plies=3, rounds=1,
                scenarios=tournament_scenarios()[-1:],
                modes=['Minimax', 'Alpha-Beta'],
                output=str(Path(tmp) / 'games.csv'),
                summary_output=str(Path(tmp) / 'summary.csv'),
            )
            self.assertEqual(len(matches), 2)
            self.assertEqual(len(summary), 2)
            self.assertTrue(all(m['result'] in ('win', 'draw', 'unfinished')
                                for m in matches))
            self.assertTrue((Path(tmp) / 'summary.csv').exists())


if __name__ == '__main__':
    unittest.main()
