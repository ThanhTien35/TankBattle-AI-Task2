import unittest
from dataclasses import replace
from tankbattle.engine.model import Action, GameState, Tank, Base, Bullet, Wall
from tankbattle.engine.game import apply_joint_actions
from tankbattle.engine.maps import get_map
from tankbattle.agents.search import SearchAgent


class SimultaneousTests(unittest.TestCase):
    def setUp(self):
        self.s = GameState((Tank(3, 3, 1, 0), Tank(5, 3, -1, 0)),
                           (Base(0, 0), Base(14, 14)), ())

    def test_two_movements_in_one_cycle(self):
        x = apply_joint_actions(self.s, Action.MOVE_UP, Action.MOVE_DOWN)
        self.assertEqual(((x.tanks[0].x,x.tanks[0].y),(x.tanks[1].x,x.tanks[1].y)), ((3,2),(5,4)))
        self.assertEqual(x.ply, 1)

    def test_both_move_same_cell_blocked(self):
        x = apply_joint_actions(self.s, Action.MOVE_RIGHT, Action.MOVE_LEFT)
        self.assertEqual([(t.x,t.y) for t in x.tanks], [(3,3),(5,3)])

    def test_both_swap_blocked(self):
        s = replace(self.s,tanks=(replace(self.s.tanks[0],x=3),replace(self.s.tanks[1],x=4)))
        x = apply_joint_actions(s, Action.MOVE_RIGHT, Action.MOVE_LEFT)
        self.assertEqual([(t.x,t.y) for t in x.tanks], [(3,3),(4,3)])

    def test_shoot_simultaneous(self):
        x=apply_joint_actions(self.s,Action.FIRE,Action.FIRE)
        self.assertEqual([t.hp for t in x.tanks],[5,5])
        self.assertIsNone(x.winner)

    def test_simultaneous_death_draw(self):
        s=replace(self.s,tanks=(replace(self.s.tanks[0],hp=1), replace(self.s.tanks[1],hp=1)))
        x=apply_joint_actions(s,Action.FIRE,Action.FIRE)
        self.assertEqual(x.winner,-1)

    def test_bullets_move_only_three_per_cycle(self):
        s=replace(self.s,tanks=(Tank(3,3,0,-1),Tank(10,10,-1,0)))
        x=apply_joint_actions(s,Action.FIRE,Action.STAY)
        self.assertEqual((x.bullets[0].x,x.bullets[0].y),(3,0))

    def test_first_three_cells_block_wall(self):
        s=replace(self.s,walls=(Wall(4,3),))
        x=apply_joint_actions(s,Action.FIRE,Action.STAY)
        self.assertEqual(x.walls[0].hp,2)

    def test_same_player_independent_decision(self):
        for mode in ('Minimax','Alpha-Beta','Heuristic Minimax','Heuristic Alpha-Beta'):
            p0=SearchAgent(mode,depth=1).choose_joint_action(self.s,0)
            p1=SearchAgent(mode,depth=1).choose_joint_action(self.s,1)
            self.assertIn(p0,tuple(Action))
            self.assertIn(p1,tuple(Action))

    def test_minimax_alpha_beta_same_strict_value(self):
        for player in (0,1):
            a=SearchAgent('Minimax',depth=2,gameplay_tactics=False)
            b=SearchAgent('Alpha-Beta',depth=2,gameplay_tactics=False)
            a.choose_joint_action(self.s,player)
            b.choose_joint_action(self.s,player)
            self.assertEqual(a.stats.score,b.stats.score)

    def test_hp_rules_unchanged(self):
        s=get_map('Classic Battlefield')
        self.assertEqual([t.hp for t in s.tanks],[6,6])
        self.assertEqual([b.hp for b in s.bases],[9,9])
        self.assertTrue(all(w.hp==3 for w in s.walls))

if __name__=='__main__':
    unittest.main()
