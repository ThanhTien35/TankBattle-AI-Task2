"""Regression tests for tactical action choice and search correctness."""
import random
import unittest
from dataclasses import replace

from agents.search import SearchAgent
from engine.game import apply_action, legal_actions
from engine.maps import MAP_NAMES, get_map
from engine.model import Action, Base, GameState, Tank


class AIBehaviorTests(unittest.TestCase):
    def test_stuck_upward_fire_is_replaced_by_movement(self):
        # Tinh huong hai tank quay len va ban vo ich
        state = get_map('Classic Battlefield')
        state = replace(
            state,
            tanks=(Tank(2, 4, 0, -1, 1), Tank(12, 4, 0, -1, 1)),
            bases=(Base(1, 5, 7), Base(13, 5, 8)),
            ply=44,
        )
        for mode in ('Minimax', 'Alpha-Beta', 'Heuristic Minimax', 'Heuristic Alpha-Beta'):
            with self.subTest(mode=mode):
                self.assertNotEqual(SearchAgent(mode, 3).choose_action(state), Action.FIRE)

    def test_strict_mode_keeps_terminal_only_baseline(self):
        state = get_map('Classic Battlefield')
        state = replace(
            state,
            tanks=(Tank(2, 4, 0, -1, 1), Tank(12, 4, 0, -1, 1)),
            bases=(Base(1, 5, 7), Base(13, 5, 8)),
            ply=44,
        )
        for mode in ('Minimax', 'Alpha-Beta'):
            strict = SearchAgent(mode, 3, gameplay_tactics=False)
            playable = SearchAgent(mode, 3, gameplay_tactics=True)
            self.assertEqual(strict.choose_action(state), Action.FIRE)
            self.assertNotEqual(playable.choose_action(state), Action.FIRE)
            self.assertEqual(strict.stats.score, playable.stats.score)

    def test_no_empty_shot_on_open_board(self):
        state = GameState(
            tanks=(Tank(5, 5, 0, -1), Tank(11, 10, -1, 0)),
            bases=(Base(1, 7), Base(13, 7)), walls=(),
        )
        for mode in ('Minimax', 'Alpha-Beta'):
            with self.subTest(mode=mode):
                self.assertNotEqual(SearchAgent(mode, 3).choose_action(state), Action.FIRE)

    def test_forced_finishing_shot_kept(self):
        state = GameState(
            tanks=(Tank(5, 5, 1, 0), Tank(7, 5, 0, -1, 1)),
            bases=(Base(1, 7), Base(13, 7)), walls=(),
        )
        for mode in ('Minimax', 'Alpha-Beta', 'Heuristic Minimax', 'Heuristic Alpha-Beta'):
            with self.subTest(mode=mode):
                self.assertEqual(SearchAgent(mode, 3).choose_action(state), Action.FIRE)

    def test_pruning_matches_minimax_in_random_reachable_states(self):
        randomizer = random.Random(2026)
        for name in MAP_NAMES:
            state = get_map(name)
            for _ in range(12):
                for plain, pruned in (('Minimax', 'Alpha-Beta'),
                                      ('Heuristic Minimax', 'Heuristic Alpha-Beta')):
                    a, b = SearchAgent(plain, 3), SearchAgent(pruned, 3)
                    aa, bb = a.choose_action(state), b.choose_action(state)
                    with self.subTest(map=name, ply=state.ply, algorithm=plain):
                        self.assertEqual(a.stats.score, b.stats.score)
                        self.assertEqual(aa, bb)
                        self.assertLessEqual(b.stats.nodes, a.stats.nodes)
                if state.terminal:
                    break
                state = apply_action(state, randomizer.choice(legal_actions(state)))

    def test_heuristic_agents_do_not_wait_or_oscillate(self):
        # Kiem tra STAY va di qua lai tren Classic Battlefield
        for depth in (2, 3, 4):
            state = get_map('Classic Battlefield')
            agents = (SearchAgent('Heuristic Minimax', depth),
                      SearchAgent('Heuristic Alpha-Beta', depth))
            moves = 0
            stays = 0
            for _ in range(70):
                if state.terminal:
                    break
                player = state.turn
                old_tank = state.tanks[player]
                action = agents[player].choose_action(state)
                stays += action == Action.STAY
                state = apply_action(state, action)
                if (state.tanks[player].x, state.tanks[player].y) != (old_tank.x, old_tank.y):
                    moves += 1
            with self.subTest(depth=depth):
                self.assertGreaterEqual(moves, 5)
                self.assertLessEqual(stays, 4)
                self.assertTrue(state.terminal)

    def test_battle_moves_and_does_not_stall(self):
        for name in MAP_NAMES:
            state = get_map(name)
            agents = (SearchAgent('Minimax', 3), SearchAgent('Alpha-Beta', 3))
            movements = 0
            empty_fire_streak = 0
            worst_streak = 0
            for _ in range(75):
                if state.terminal:
                    break
                player = state.turn
                tank = state.tanks[player]
                action = agents[player].choose_action(state)
                events = []
                state = apply_action(state, action, events=events)
                if action in (Action.MOVE_UP, Action.MOVE_DOWN, Action.MOVE_LEFT, Action.MOVE_RIGHT):
                    if (tank.x, tank.y) != (state.tanks[player].x, state.tanks[player].y):
                        movements += 1
                if action == Action.FIRE and not any('hit ' in e for e in events):
                    empty_fire_streak += 1
                else:
                    empty_fire_streak = 0
                worst_streak = max(worst_streak, empty_fire_streak)
            with self.subTest(map=name):
                self.assertGreaterEqual(movements, 4)
                self.assertLessEqual(worst_streak, 10)
                self.assertTrue(state.terminal or state.ply == 75)


if __name__ == '__main__':
    unittest.main()
