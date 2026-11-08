import unittest
from dataclasses import replace
from engine.model import Action, Bullet, GameState, Tank, Base, Wall, initial_state
from engine.game import apply_action, legal_actions
from agents.search import SearchAgent


class GameRuleTests(unittest.TestCase):
    def test_initial_health_and_actions(self):
        state = initial_state()
        self.assertEqual([t.hp for t in state.tanks], [6, 6])
        self.assertEqual([b.hp for b in state.bases], [9, 9])
        self.assertTrue(all(w.hp == 3 for w in state.walls))
        self.assertIn(Action.FIRE, legal_actions(state))
        self.assertIn(Action.STAY, legal_actions(state))

    def test_move_exactly_one_cell_and_facing(self):
        s = apply_action(initial_state(), Action.MOVE_UP)
        self.assertEqual((s.tanks[0].x, s.tanks[0].y), (2, 4))
        self.assertEqual((s.tanks[0].dx, s.tanks[0].dy), (0, -1))
        self.assertEqual(s.turn, 1)

    def test_bullet_moves_three_cells_per_cycle(self):
        s = apply_action(initial_state(), Action.FIRE)
        self.assertEqual((s.bullets[0].x, s.bullets[0].y), (5, 5))

    def test_bullet_hits_wall_after_each_cell(self):
        s = initial_state()
        s = replace(s, bullets=(Bullet(5, 5, 1, 0, 0),))
        s = apply_action(s, Action.STAY)
        wall = next(w for w in s.walls if (w.x, w.y) == (7, 5))
        self.assertEqual(wall.hp, 2)
        self.assertEqual(len(s.bullets), 0)

    def test_destroy_tank_ends_match(self):
        s = initial_state()
        tanks = (s.tanks[0], replace(s.tanks[1], hp=1))
        s = replace(s, tanks=tanks, bullets=(Bullet(11, 5, 1, 0, 0),))
        s = apply_action(s, Action.STAY)
        self.assertEqual(s.winner, 0)
        self.assertTrue(s.terminal)

    def test_bullet_cannot_skip_intermediate_wall(self):
        s = initial_state()
        s = replace(s, walls=(Wall(4, 5, 1),), bullets=(Bullet(2, 5, 1, 0, 0),))
        s = apply_action(s, Action.STAY)
        self.assertEqual(s.tanks[1].hp, 6)
        self.assertFalse(s.walls)
        self.assertFalse(s.bullets)

    def test_minimax_alpha_beta_equivalent_scores(self):
        s = initial_state()
        a, b = SearchAgent('Minimax', 3), SearchAgent('Alpha-Beta', 3)
        self.assertEqual(a.choose_action(s), b.choose_action(s))
        self.assertEqual(a.stats.score, b.stats.score)
        self.assertLessEqual(b.stats.nodes, a.stats.nodes)

    def test_heuristic_alpha_beta_equivalent_scores(self):
        s = initial_state()
        a, b = SearchAgent('Heuristic Minimax', 3), SearchAgent('Heuristic Alpha-Beta', 3)
        self.assertEqual(a.choose_action(s), b.choose_action(s))
        self.assertEqual(a.stats.score, b.stats.score)
        self.assertLessEqual(b.stats.nodes, a.stats.nodes)


if __name__ == '__main__':
    unittest.main()

class IntegrationTests(unittest.TestCase):
    def test_external_agent_contract(self):
        from agents.registry import ExternalAgent
        s = initial_state()
        a = ExternalAgent('external_agents.example_agent').choose_action(s)
        self.assertIn(a, legal_actions(s))

    def test_base_destroyed_ends_match(self):
        s = initial_state()
        bases = (s.bases[0], replace(s.bases[1], hp=1))
        s = replace(s, bases=bases, bullets=(Bullet(12, 5, 1, 0, 0),))
        s = apply_action(s, Action.STAY)
        self.assertEqual(s.winner, 0)
        self.assertEqual(s.reason, 'Base destroyed')

    def test_blocked_move_spends_turn_but_updates_facing(self):
        s = initial_state()
        s = replace(s, walls=s.walls + (Wall(2, 4),))
        s2 = apply_action(s, Action.MOVE_UP)
        self.assertEqual((s2.tanks[0].x, s2.tanks[0].y), (2, 5))
        self.assertEqual((s2.tanks[0].dx, s2.tanks[0].dy), (0, -1))
        self.assertEqual(s2.ply, 1)
