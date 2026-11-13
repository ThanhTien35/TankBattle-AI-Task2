"""Four simultaneous-game search modes using pure maximin of action pairs.

Depth counts FULL cycles. Alpha-Beta prunes maximin branches; Heuristic
variants evaluate nonterminal states. A root-level gameplay preference may
be enabled for more active demos; --strict-search removes it.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from time import perf_counter

from tankbattle.engine.game import apply_joint_actions, legal_actions
from tankbattle.engine.model import Action, GameState, HEIGHT, WIDTH

MODES = ('Minimax', 'Alpha-Beta', 'Heuristic Minimax', 'Heuristic Alpha-Beta')


@dataclass
class SearchStats:
    algorithm: str = ''
    elapsed_ms: float = 0.0
    nodes: int = 0
    leaves: int = 0
    prunes: int = 0
    depth: int = 0
    score: float = 0.0
    selection_score: float = 0.0
    action: str = ''


def _distance(a, b) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def _direction(a, b) -> tuple[int, int]:
    return ((b.x > a.x) - (b.x < a.x),
            (b.y > a.y) - (b.y < a.y))


def _first_impact(state: GameState, player: int):
    """First object hit by a shot from the player's current position."""
    tank = state.tanks[player]
    walls = {(w.x, w.y): w for w in state.walls}
    x, y = tank.x, tank.y
    while True:
        x += tank.dx
        y += tank.dy
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            return 'empty', None
        if (x, y) in walls:
            return 'wall', walls[(x, y)]
        for j, other in enumerate(state.tanks):
            if other.hp > 0 and (x, y) == (other.x, other.y):
                return ('enemy_tank' if j != player else 'own_tank'), other
        for j, base in enumerate(state.bases):
            if base.hp > 0 and (x, y) == (base.x, base.y):
                return ('enemy_base' if j != player else 'own_base'), base


def _wall_on_attack_lane(state: GameState, player: int, wall) -> bool:
    tank = state.tanks[player]
    for target in (state.tanks[1 - player], state.bases[1 - player]):
        if tank.x == target.x == wall.x:
            if (target.y - tank.y) * (wall.y - tank.y) > 0 and abs(wall.y - tank.y) < abs(target.y - tank.y):
                return True
        if tank.y == target.y == wall.y:
            if (target.x - tank.x) * (wall.x - tank.x) > 0 and abs(wall.x - tank.x) < abs(target.x - tank.x):
                return True
    return False


def _shot_value(state: GameState, player: int) -> float:
    kind, obj = _first_impact(state, player)
    if kind == 'enemy_tank':
        return 95.0 + (75.0 if obj.hp == 1 else 0.0)
    if kind == 'enemy_base':
        return 100.0 + (75.0 if obj.hp == 1 else 0.0)
    if kind in ('own_tank', 'own_base'):
        return -160.0
    if kind == 'wall':
        # Chi uu tien pha tuong neu tuong chan duong tan cong
        return (23.0 + (3 - obj.hp) * 5.0) if _wall_on_attack_lane(state, player, obj) else -65.0
    return -95.0


@lru_cache(maxsize=8192)
def _attack_distance(start: tuple[int, int], target: tuple[int, int],
                     walls: frozenset[tuple[int, int]],
                     blocked: frozenset[tuple[int, int]]) -> int:
    """Walking distance to a square with a clear shooting lane to target."""
    def can_shoot(x: int, y: int) -> bool:
        tx, ty = target
        if (x, y) == target or (x != tx and y != ty):
            return False
        dx = (tx > x) - (tx < x)
        dy = (ty > y) - (ty < y)
        x += dx
        y += dy
        while (x, y) != target:
            if (x, y) in walls or (x, y) in blocked:
                return False
            x += dx
            y += dy
        return True

    q = deque([(start[0], start[1], 0)])
    visited = {start}
    while q:
        x, y, steps = q.popleft()
        if can_shoot(x, y):
            return steps
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = x + dx, y + dy
            if (0 <= nx < WIDTH and 0 <= ny < HEIGHT
                    and (nx, ny) not in visited
                    and (nx, ny) not in walls
                    and (nx, ny) not in blocked):
                visited.add((nx, ny))
                q.append((nx, ny, steps + 1))
    return 20


def _attack_route(state: GameState, player: int, target_player: int, is_base: bool) -> int:
    own = state.tanks[player]
    target = state.bases[target_player] if is_base else state.tanks[target_player]
    walls = frozenset((w.x, w.y) for w in state.walls)
    # Khong di qua tank va base; chi cho phep dung tai vi tri hien tai
    occupied = frozenset(
        (o.x, o.y) for o in (*state.tanks, *state.bases)
        if o.hp > 0 and (o.x, o.y) != (own.x, own.y)
    )
    return _attack_distance((own.x, own.y), (target.x, target.y), walls, occupied)


def _incoming_threat(state: GameState, player: int) -> float:
    tank, base = state.tanks[player], state.bases[player]
    walls = {(w.x, w.y) for w in state.walls}
    other_units = {(o.x, o.y) for o in (*state.tanks, *state.bases) if o.hp > 0}
    risk = 0.0
    for bullet in state.bullets:
        x, y = bullet.x, bullet.y
        for _ in range(3):
            x += bullet.dx
            y += bullet.dy
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT) or (x, y) in walls:
                break
            if (x, y) == (tank.x, tank.y):
                risk += 125.0 + (170.0 if tank.hp <= 1 else 0.0)
                break
            if (x, y) == (base.x, base.y):
                risk += 95.0 + (130.0 if base.hp <= 1 else 0.0)
                break
            if (x, y) in other_units:
                break
    return risk


def _position_score(state: GameState, player: int) -> float:
    own = state.tanks[player]
    enemy = state.tanks[1 - player]
    base = state.bases[1 - player]
    base_route = _attack_route(state, player, 1 - player, True)
    tank_route = _attack_route(state, player, 1 - player, False)
    kind, _ = _first_impact(state, player)
    shot_bonus = {'enemy_base': 65.0, 'enemy_tank': 52.0, 'wall': 0.0}.get(kind, 0.0)
    mobility = sum(1 for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))
                   if 0 <= own.x + dx < WIDTH and 0 <= own.y + dy < HEIGHT
                   and not any((obj.x, obj.y) == (own.x + dx, own.y + dy)
                               for obj in (*state.walls, *state.bases, state.tanks[1 - player])))
    return (-8.0 * base_route - 4.0 * tank_route
            - 1.2 * _distance(own, base) - 0.8 * _distance(own, enemy)
            + shot_bonus + 2.0 * mobility - _incoming_threat(state, player))


# THUAT TOAN: HAM DANH GIA TRANG THAI (HEURISTIC EVALUATION)
# Minimax thuong chi cham diem trang thai terminal; heuristic dung HP va vi tri.
def evaluate(state: GameState, root_player: int, heuristic: bool) -> float:
    if state.winner is not None:
        if state.winner == -1:
            return 0.0
        return (100000.0 - state.ply) if state.winner == root_player else (-100000.0 + state.ply)
    if not heuristic:
        # Minimax thuong chi cham diem trang thai ket thuc
        return 0.0
    t0, t1 = state.tanks
    b0, b1 = state.bases
    score = (115.0 * (t0.hp - t1.hp) + 135.0 * (b0.hp - b1.hp)
             + _position_score(state, 0) - _position_score(state, 1))
    return score if root_player == 0 else -score


# THUAT TOAN 1: MINIMAX (MAXIMIN) - max action cua ta, min action doi thu.
# THUAT TOAN 2: ALPHA-BETA - cat nhanh voi hai can alpha, beta.
# THUAT TOAN 3: HEURISTIC MINIMAX - Minimax va ham danh gia.
# THUAT TOAN 4: HEURISTIC ALPHA-BETA - ket hop cat nhanh va heuristic.
# Ca bon dung chung lop; tuy chon use_pruning va use_heuristic.
def replace_root_turn(state: GameState, player: int) -> GameState:
    from dataclasses import replace
    return replace(state, turn=player)


class SearchAgent:
    def __init__(self, mode: str = 'Heuristic Alpha-Beta', depth: int = 3,
                 gameplay_tactics: bool = True):
        if mode not in MODES:
            raise ValueError(f'Unknown mode: {mode}. Choose from {MODES}')
        if not 1 <= depth <= 6:
            raise ValueError('Depth must be 1..6 (4+ may be slow)')
        self.mode = mode
        self.depth = depth
        self.stats = SearchStats(algorithm=mode, depth=depth)
        self.use_pruning = mode in ('Alpha-Beta', 'Heuristic Alpha-Beta')
        self.use_heuristic = mode in ('Heuristic Minimax', 'Heuristic Alpha-Beta')
        self.gameplay_tactics = gameplay_tactics
        self._recent_poses = deque(maxlen=10)
        self._last_ply = -1

    # HO TRO GAMEPLAY: uu tien nuoc di co ich, khong thay doi luat game.
    def _root_rank(self, state: GameState, action: Action, after: GameState) -> float:
        player = state.turn
        before_tank, after_tank = state.tanks[player], after.tanks[player]
        old_pos = (before_tank.x, before_tank.y, before_tank.dx, before_tank.dy)
        new_pos = (after_tank.x, after_tank.y, after_tank.dx, after_tank.dy)
        before = evaluate(state, player, True)
        after_score = evaluate(after, player, True)
        rank = 0.30 * (after_score - before)
        if action == Action.FIRE:
            quality = _shot_value(state, player)
            rank += quality
            if quality < 0:
                rank -= 30.0 * self._recent_poses.count(old_pos)
        elif action == Action.STAY:
            rank -= 45.0
        elif (after_tank.x, after_tank.y) == (before_tank.x, before_tank.y):
            rank -= 45.0
        else:
            rank += 8.0
        # Giam lap vi tri cu, khong phat neu dang ban trung muc tieu
        if action != Action.FIRE or _shot_value(state, player) <= 0:
            rank -= 16.0 * self._recent_poses.count(new_pos)
        return rank

    # SIMULTANEOUS MAXIMIN: moi agent tu chon action tu cung state.
    # Minimax/Alpha-Beta duoc ap dung tren ma tran cap action 6x6.
    # Day la pure-strategy worst-case maximin, KHONG phai mixed Nash.
    def choose_joint_action(self, state: GameState, player: int) -> Action:
        if state.terminal:
            return Action.STAY
        if state.ply <= self._last_ply:
            self._recent_poses.clear()
        start = perf_counter()
        self.stats = SearchStats(algorithm=self.mode, depth=self.depth, nodes=1)
        actions = legal_actions(state)
        alpha = float('-inf')
        best_action, best_score, best_selection = Action.STAY, float('-inf'), float('-inf')
        ranked = []
        for action in actions:
            joint = (action, Action.STAY) if player == 0 else (Action.STAY, action)
            next_state = apply_joint_actions(state, *joint)
            tactical = replace_root_turn(state, player)
            rank = self._root_rank(tactical, action, replace_root_turn(next_state, player)) if self.gameplay_tactics else 0.0
            ranked.append((rank, action))
        if self.gameplay_tactics:
            ranked.sort(key=lambda x: x[0], reverse=True)

        for rank, action in ranked:
            worst = float('inf')
            for response in actions:
                a0, a1 = ((action, response) if player == 0 else (response, action))
                child = apply_joint_actions(state, a0, a1)
                score = self._joint_search(child, self.depth - 1, player,
                                           alpha if self.use_pruning else float('-inf'),
                                           worst if self.use_pruning else float('inf'))
                worst = min(worst, score)
                if self.use_pruning and worst <= alpha:
                    self.stats.prunes += 1
                    break
            selection = (worst + 0.65 * max(-250., min(250., rank))
                         if self.gameplay_tactics and self.use_heuristic else worst)
            if selection > best_selection:
                best_action, best_score, best_selection = action, worst, selection
            if self.use_pruning and not (self.gameplay_tactics and self.use_heuristic):
                alpha = max(alpha, worst)
        self.stats.elapsed_ms = (perf_counter() - start) * 1000
        self.stats.score = best_score
        self.stats.selection_score = best_selection
        self.stats.action = best_action.value
        tank = state.tanks[player]
        if self.gameplay_tactics:
            self._recent_poses.append((tank.x, tank.y, tank.dx, tank.dy))
        self._last_ply = state.ply
        return best_action

    def _joint_search(self, state: GameState, depth: int, player: int,
                      alpha: float, beta: float) -> float:
        self.stats.nodes += 1
        if depth == 0 or state.terminal:
            self.stats.leaves += 1
            return evaluate(state, player, self.use_heuristic)
        best = float('-inf')
        for action in legal_actions(state):
            worst = float('inf')
            for response in legal_actions(state):
                a0, a1 = ((action, response) if player == 0 else (response, action))
                child = apply_joint_actions(state, a0, a1)
                value = self._joint_search(child, depth - 1, player, alpha, min(beta, worst))
                worst = min(worst, value)
                if self.use_pruning and worst <= alpha:
                    self.stats.prunes += 1
                    break
            best = max(best, worst)
            if self.use_pruning:
                alpha = max(alpha, best)
                if alpha >= beta:
                    self.stats.prunes += 1
                    break
        return best

