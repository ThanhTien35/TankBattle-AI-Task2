"""Deterministic turn-based rules, used identically by UI and AI simulation.

Design decision (not specified by assignment): one action constitutes one game
cycle. Players alternate; after every action, all active bullets advance up to
three cells, checking collisions after EACH cell. A blocked move still spends a
turn and changes the tank's facing. There is a 160-ply draw safeguard.
"""
from __future__ import annotations
from dataclasses import replace
from tankbattle.engine.model import Action, DIRECTIONS, GameState, Bullet, MAX_TURNS, WIDTH, HEIGHT


def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < WIDTH and 0 <= y < HEIGHT


def occupied(state: GameState, x: int, y: int) -> bool:
    return (any(w.hp > 0 and (w.x, w.y) == (x, y) for w in state.walls)
            or any(t.hp > 0 and (t.x, t.y) == (x, y) for t in state.tanks)
            or any(b.hp > 0 and (b.x, b.y) == (x, y) for b in state.bases))


def legal_actions(state: GameState) -> tuple[Action, ...]:
    if state.terminal:
        return ()
    # Du 6 action; MOVE bi chan van doi huong va ton mot luot
    return (Action.FIRE, Action.MOVE_UP, Action.MOVE_DOWN,
            Action.MOVE_LEFT, Action.MOVE_RIGHT, Action.STAY)


def _check_winner(tanks, bases) -> tuple[int | None, str]:
    defeated = [i for i in (0, 1) if tanks[i].hp <= 0 or bases[i].hp <= 0]
    if len(defeated) == 2:
        return -1, 'Both sides destroyed'
    if defeated:
        loser = defeated[0]
        reason = 'Tank destroyed' if tanks[loser].hp <= 0 else 'Base destroyed'
        return 1 - loser, reason
    return None, ''


def apply_action(state: GameState, action: Action | str,
                 events: list[str] | None = None) -> GameState:
    # events chi duoc ghi khi UI yeu cau, AI van dung cung logic
    def emit(message: str) -> None:
        if events is not None:
            events.append(message)

    if state.terminal:
        return state
    action = Action(action)
    tanks, bases, walls, bullets = list(state.tanks), list(state.bases), list(state.walls), list(state.bullets)
    player = state.turn
    tank = tanks[player]
    if action in DIRECTIONS:
        dx, dy = DIRECTIONS[action]
        nx, ny = tank.x + dx, tank.y + dy
        if in_bounds(nx, ny) and not occupied(state, nx, ny):
            tank = replace(tank, x=nx, y=ny)
            emit(f'P{player + 1} moved to ({nx},{ny})')
        else:
            emit(f'P{player + 1} move blocked')
        tanks[player] = replace(tank, dx=dx, dy=dy)
    elif action == Action.FIRE:
        bullets.append(Bullet(tank.x, tank.y, tank.dx, tank.dy, player))
        emit(f'P{player + 1} fired')

    # Dan di tung o, kiem tra va cham ngay sau moi o
    moving = []
    for bullet in bullets:
        x, y = bullet.x, bullet.y
        active = True
        for _ in range(3):
            x += bullet.dx
            y += bullet.dy
            if not in_bounds(x, y):
                active = False
                break
            hit = False
            for j, wall in enumerate(walls):
                if wall.hp > 0 and (wall.x, wall.y) == (x, y):
                    walls[j] = replace(wall, hp=wall.hp - 1)
                    emit(f'P{bullet.owner + 1} hit wall ({x},{y}): {wall.hp}->{wall.hp - 1}')
                    hit = True
                    break
            if not hit:
                for j, target in enumerate(tanks):
                    if target.hp > 0 and (target.x, target.y) == (x, y):
                        tanks[j] = replace(target, hp=target.hp - 1)
                        emit(f'P{bullet.owner + 1} hit P{j + 1} Tank: {target.hp}->{target.hp - 1}')
                        hit = True
                        break
            if not hit:
                for j, base in enumerate(bases):
                    if base.hp > 0 and (base.x, base.y) == (x, y):
                        bases[j] = replace(base, hp=base.hp - 1)
                        emit(f'P{bullet.owner + 1} hit P{j + 1} Base: {base.hp}->{base.hp - 1}')
                        hit = True
                        break
            if hit:
                active = False
                winner, reason = _check_winner(tanks, bases)
                if winner is not None:
                    emit(f'GAME OVER: {"Draw" if winner == -1 else f"P{winner + 1} wins"} ({reason})')
                    return GameState(tuple(tanks), tuple(bases), tuple(w for w in walls if w.hp > 0),
                                     tuple(moving), 1 - player, state.ply + 1, winner, reason)
                break
        if active:
            moving.append(replace(bullet, x=x, y=y))
    winner, reason = _check_winner(tanks, bases)
    next_ply = state.ply + 1
    if winner is None and next_ply >= MAX_TURNS:
        winner, reason = -1, f'{MAX_TURNS}-turn limit'
    if winner is not None:
        emit(f'GAME OVER: {"Draw" if winner == -1 else f"P{winner + 1} wins"} ({reason})')
    return GameState(tuple(tanks), tuple(bases), tuple(w for w in walls if w.hp > 0),
                     tuple(moving), 1 - player, next_ply, winner, reason)
