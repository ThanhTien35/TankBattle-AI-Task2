"""Pixel art asset and layout checks without a PyGame dependency."""
from pathlib import Path
import struct
import unittest
from engine.model import WIDTH, HEIGHT, initial_state

ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'pixel'

class PixelUiAssetTests(unittest.TestCase):
    def test_board_is_square(self):
        self.assertEqual((WIDTH, HEIGHT), (15, 15))

    def test_all_required_sprites_exist_and_are_32x32_png(self):
        names = ['brick', 'steel', 'flash', 'base_blue', 'base_gold']
        names += [f'forest_{i}' for i in range(4)]
        names += [f'tank_{side}_{direction}' for side in ('blue', 'gold')
                  for direction in ('up', 'down', 'left', 'right')]
        for name in names:
            with self.subTest(sprite=name):
                data = (ROOT / f'{name}.png').read_bytes()
                self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
                self.assertEqual(struct.unpack('>II', data[16:24]), (32, 32))

    def test_wall_visual_kinds_follow_same_game_rule(self):
        state = initial_state()
        self.assertEqual({w.kind for w in state.walls}, {'brick', 'steel'})
        self.assertTrue(all(w.hp == 3 for w in state.walls))
        self.assertTrue(all(0 <= w.x < WIDTH and 0 <= w.y < HEIGHT for w in state.walls))

if __name__ == '__main__':
    unittest.main()
