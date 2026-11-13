"""Simultaneous Tank Battle rules shared by AI, GUI, and benchmarks.

One game cycle: both choose actions independently from the same state, both
movements are resolved, both shots spawn, then bullets advance at most three
cells. The HP rules remain unchanged. A 160-cycle draw is a demo safeguard.
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


def apply_joint_actions(state: GameState, action0: Action | str, action1: Action | str,
                        events: list[str] | None = None) -> GameState:
    """Simultaneous cycle: both actions use the SAME original state.

    Movement is resolved together, then shots are spawned and all bullets
    advance 3 cells in 3 simultaneous substeps. Damage in the same substep
    is applied together so neither player gets an artificial first-shot edge.
    """
    if state.terminal:
        return state
    actions = (Action(action0), Action(action1))
    tanks = list(state.tanks)
    bases = list(state.bases)
    walls = list(state.walls)
    bullets = list(state.bullets)

    def emit(msg):
        if events is not None:
            events.append(msg)

    # THUAT TOAN: XU LY DI CHUYEN DONG THOI
    occupied_static = {(w.x, w.y) for w in walls if w.hp > 0}
    occupied_static.update((b.x, b.y) for b in bases if b.hp > 0)
    starts = [(t.x, t.y) for t in tanks]
    dests = list(starts)
    for p, action in enumerate(actions):
        if action in DIRECTIONS:
            dx, dy = DIRECTIONS[action]
            tanks[p] = replace(tanks[p], dx=dx, dy=dy)
            dest = (starts[p][0] + dx, starts[p][1] + dy)
            if in_bounds(*dest) and dest not in occupied_static:
                dests[p] = dest
    # Two tanks cannot occupy a cell, swap cells or move into a stationary tank.
    if dests[0] == dests[1] or (dests[0] == starts[1] and dests[1] == starts[0]):
        dests = starts.copy()
    else:
        for p in (0, 1):
            if dests[p] == starts[1 - p] and dests[1 - p] == starts[1 - p]:
                dests[p] = starts[p]
    for p in (0, 1):
        if actions[p] in DIRECTIONS:
            if dests[p] == starts[p]:
                emit(f'P{p + 1} move blocked')
            else:
                emit(f'P{p + 1} moved to {dests[p]}')
        tanks[p] = replace(tanks[p], x=dests[p][0], y=dests[p][1])

    # Both FIRE actions are registered before any bullet advances.
    for p, action in enumerate(actions):
        if action == Action.FIRE:
            old_tank = state.tanks[p]
            bullets.append(Bullet(old_tank.x, old_tank.y, old_tank.dx, old_tank.dy, p))
            emit(f'P{p + 1} fired')

    # THUAT TOAN: CAP NHAT DAN DONG THOI THEO TUNG O
    for _ in range(3):
        next_bullets = []
        hits = {'wall': {}, 'tank': {}, 'base': {}}
        wall_by_pos = {(w.x, w.y): i for i, w in enumerate(walls) if w.hp > 0}
        tank_by_pos = {(t.x, t.y): i for i, t in enumerate(tanks) if t.hp > 0}
        base_by_pos = {(b.x, b.y): i for i, b in enumerate(bases) if b.hp > 0}
        for bullet in bullets:
            x, y = bullet.x + bullet.dx, bullet.y + bullet.dy
            if not in_bounds(x, y):
                continue
            pos = (x, y)
            for kind, mapping in (('wall', wall_by_pos), ('tank', tank_by_pos), ('base', base_by_pos)):
                if pos in mapping:
                    idx = mapping[pos]
                    hits[kind][idx] = hits[kind].get(idx, 0) + 1
                    emit(f'P{bullet.owner + 1} hit {kind} {idx + 1}')
                    break
            else:
                next_bullets.append(replace(bullet, x=x, y=y))
        # Hits in one substep are committed simultaneously.
        for idx, damage in hits['wall'].items():
            walls[idx] = replace(walls[idx], hp=max(0, walls[idx].hp - damage))
        for idx, damage in hits['tank'].items():
            tanks[idx] = replace(tanks[idx], hp=max(0, tanks[idx].hp - damage))
        for idx, damage in hits['base'].items():
            bases[idx] = replace(bases[idx], hp=max(0, bases[idx].hp - damage))
        bullets = next_bullets
        winner, reason = _check_winner(tanks, bases)
        if winner is not None:
            break

    winner, reason = _check_winner(tanks, bases)
    cycle = state.ply + 1
    if winner is None and cycle >= MAX_TURNS:
        winner, reason = -1, f'{MAX_TURNS}-cycle limit'
    if winner is not None:
        emit(f'GAME OVER: {"Draw" if winner == -1 else f"P{winner + 1} wins"} ({reason})')
    return GameState(tuple(tanks), tuple(bases), tuple(w for w in walls if w.hp > 0),
                     tuple(bullets), 0, cycle, winner, reason)
