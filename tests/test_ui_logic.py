"""Exercise replay controls without requiring a graphical SDL session."""
from __future__ import annotations
import importlib.util
import csv
import tempfile
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from tankbattle.agents.search import SearchAgent
from tankbattle.engine.maps import MAP_NAMES, get_map


class UILogicTests(unittest.TestCase):
    def _load_without_pygame(self):
        # Gia lap pygame.time de test replay khi khong co man hinh
        fake = types.ModuleType('pygame')
        fake.Rect = object
        fake.time = types.SimpleNamespace(get_ticks=lambda: 1000)
        module_name = '_tank_ui_test_module'
        file = Path(__file__).resolve().parents[1] / 'tankbattle' / 'ui' / 'pygame_app.py'
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'pygame': fake, module_name: module}):
            spec.loader.exec_module(module)
        return module

    def test_replay_navigation_preserves_live_match(self):
        module = self._load_without_pygame()
        app = module.BattleApp.__new__(module.BattleApp)
        app.starting_state = get_map('Open Arena')
        app.state = app.starting_state
        app.map_name = app.scenario_name = 'Open Arena'
        app.depth = 2
        app.external_modules = ('tankbattle.external_agents.example_agent', 'tankbattle.external_agents.example_agent')
        app.modes = ['Minimax', 'Alpha-Beta']
        app.agents = [SearchAgent('Minimax', 2), SearchAgent('Alpha-Beta', 2)]
        app.interval = 600
        app._reset()
        app._step()
        app._step()
        self.assertEqual(len(app.history), 3)
        self.assertEqual(len(app.records), 2)
        with tempfile.TemporaryDirectory() as tmp:
            module.__file__ = str(Path(tmp) / 'tankbattle' / 'ui' / 'pygame_app.py')
            app._save_log()
            exported = list((Path(tmp) / 'results' / 'battle_logs').glob('*.csv'))
            self.assertEqual(len(exported), 1)
            with exported[0].open(encoding='utf-8-sig') as f:
                self.assertEqual(len(list(csv.DictReader(f))), 2)
        final = app.state
        app._open_replay()
        self.assertTrue(app.replay_mode)
        app._handle_button('prev')
        self.assertEqual(app.display_state.ply, 1)
        self.assertEqual(app.state, final)
        app._step()
        self.assertEqual(app.display_state.ply, 2)
        app._handle_button('exit_replay')
        self.assertFalse(app.replay_mode)
        self.assertEqual(app.state, final)
        app._change_map()
        self.assertEqual(app.map_name, 'Tactical Maze')
        self.assertEqual(len(app.history), 1)
        self.assertEqual(len(app.records), 0)
        self.assertEqual(app.state.ply, 0)


if __name__ == '__main__':
    unittest.main()
