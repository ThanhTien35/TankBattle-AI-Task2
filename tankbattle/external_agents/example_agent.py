"""Example plug-in API for a different student group. No pygame required."""
from tankbattle.engine.model import Action, GameState
from tankbattle.engine.game import legal_actions


def choose_action(state: GameState) -> Action:
    legal = legal_actions(state)
    tank = state.tanks[state.turn]
    target = state.tanks[1 - state.turn]
    if tank.y == target.y and Action.FIRE in legal:
        return Action.FIRE
    if tank.y < target.y and Action.MOVE_DOWN in legal:
        return Action.MOVE_DOWN
    if tank.y > target.y and Action.MOVE_UP in legal:
        return Action.MOVE_UP
    if tank.x < target.x and Action.MOVE_RIGHT in legal:
        return Action.MOVE_RIGHT
    if tank.x > target.x and Action.MOVE_LEFT in legal:
        return Action.MOVE_LEFT
    return Action.STAY
