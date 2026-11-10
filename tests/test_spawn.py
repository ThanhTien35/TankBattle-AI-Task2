"""Balanced and reproducible random-spawn regression tests."""
import unittest
from tankbattle.engine.maps import MAP_NAMES, get_map, spawn_state
from tankbattle.engine.model import WIDTH, HEIGHT
from tankbattle.engine.game import apply_action
from tankbattle.engine.model import Action


class SpawnTests(unittest.TestCase):
    def check_state(self, state):
        # HP luon dung theo de bai.
        self.assertEqual([t.hp for t in state.tanks], [6, 6])
        self.assertEqual([b.hp for b in state.bases], [9, 9])
        self.assertTrue(all(w.hp == 3 for w in state.walls))
        locations = [(t.x, t.y) for t in state.tanks]
        locations += [(b.x, b.y) for b in state.bases]
        locations += [(w.x, w.y) for w in state.walls]
        self.assertEqual(len(locations), len(set(locations)))
        self.assertTrue(all(0 <= x < WIDTH and 0 <= y < HEIGHT for x, y in locations))
        a, b = state.tanks
        self.assertNotEqual(a.y, b.y)
        self.assertGreaterEqual(abs(a.x - b.x) + abs(a.y - b.y), 8)
        for player in (0, 1):
            s = state if player == 0 else type(state)(
                tanks=state.tanks, bases=state.bases, walls=state.walls,
                bullets=state.bullets, turn=1, ply=state.ply,
                winner=state.winner, reason=state.reason,
            )
            # Khong gay sat thuong Tank ngay tu vien dan dau tien.
            after = apply_action(s, Action.FIRE)
            self.assertEqual([t.hp for t in after.tanks], [6, 6])

    def test_balanced_spawn_each_map(self):
        for name in MAP_NAMES:
            with self.subTest(map=name):
                self.check_state(get_map(name))

    def test_random_spawn_30_seeds_per_map(self):
        for name in MAP_NAMES:
            for seed in range(30):
                with self.subTest(map=name, seed=seed):
                    self.check_state(spawn_state(name, 'random', seed))

    def test_random_seed_reproducible(self):
        for name in MAP_NAMES:
            self.assertEqual(spawn_state(name, 'random', 2026),
                             spawn_state(name, 'random', 2026))

    def test_invalid_spawn_mode_rejected(self):
        with self.assertRaises(ValueError):
            spawn_state('Open Arena', 'anything', 1)


if __name__ == '__main__':
    unittest.main()
