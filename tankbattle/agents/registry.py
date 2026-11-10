"""Load an external agent with `choose_action(state)` from a Python module."""
from __future__ import annotations
import importlib
from tankbattle.engine.model import Action, GameState
from tankbattle.engine.game import legal_actions

class ExternalAgent:
    def __init__(self, module_path: str = 'tankbattle.external_agents.example_agent'):
        self.module_path = module_path
        module = importlib.import_module(module_path)
        if not callable(getattr(module, 'choose_action', None)):
            raise TypeError(f'{module_path} must expose choose_action(state)')
        self._choose = module.choose_action

    def choose_action(self, state: GameState) -> Action:
        # Kiem tra action cua agent ben ngoai
        try:
            action = Action(self._choose(state))
        except (ValueError, TypeError) as exc:
            raise ValueError(f'{self.module_path} returned an invalid action') from exc
        if action not in legal_actions(state):
            raise ValueError(f'{self.module_path} returned illegal action {action.value}')
        return action
