"""Three independent, deterministic 15x15 maps for the same game rules."""
from __future__ import annotations
from dataclasses import replace
from random import Random
from tankbattle.engine.model import Base, GameState, Tank, Wall, WIDTH, HEIGHT, initial_state

MAP_NAMES = ('Classic Battlefield', 'Open Arena', 'Tactical Maze')


def _make_state(wall_coords: set[tuple[int, int]], steel: set[tuple[int, int]],
                tanks: tuple[Tank, Tank], bases: tuple[Base, Base]) -> GameState:
    # Kiem tra map truoc khi tao GameState
    objects = [(t.x, t.y) for t in tanks] + [(b.x, b.y) for b in bases]
    if len(set(objects)) != 4 or set(objects) & wall_coords:
        raise ValueError('Map has overlapping entities')
    if not all(0 <= x < WIDTH and 0 <= y < HEIGHT for x, y in wall_coords | set(objects)):
        raise ValueError('Map has out-of-bounds entities')
    walls = tuple(Wall(x, y, kind='steel' if (x, y) in steel else 'brick')
                  for x, y in sorted(wall_coords, key=lambda p: (p[1], p[0])))
    return GameState(tanks=tanks, bases=bases, walls=walls)


def get_map(name: str) -> GameState:
    if name == 'Classic Battlefield':
        # Spawn lech hang, tranh hai tank ban thang vao nhau khi bat dau.
        classic = initial_state()
        return replace(classic, tanks=(Tank(2, 3, 1, 0), Tank(12, 7, -1, 0)))
    if name == 'Open Arena':
        steel = {(6, 2), (8, 2), (6, 12), (8, 12)}
        brick = {(3, 3), (11, 3), (3, 11), (11, 11), (7, 4), (7, 10),
                 (5, 6), (9, 6), (5, 8), (9, 8)}
        return _make_state(
            steel | brick, steel,
            (Tank(2, 4, 1, 0), Tank(12, 10, -1, 0)),
            (Base(1, 7), Base(13, 7)),
        )
    if name == 'Tactical Maze':
        # Hanh lang doi xung, co loi di quanh cac buc tuong
        vertical = {(x, y) for x in (4, 10) for y in range(1, 14)
                    if y not in (3, 7, 11)}
        horizontal = {(x, y) for y in (3, 11) for x in range(5, 10)
                      if x not in (6, 8)}
        brick = vertical | horizontal | {(7, 5), (7, 9), (2, 3), (12, 3),
                                         (2, 11), (12, 11), (6, 1), (8, 1),
                                         (6, 13), (8, 13)}
        steel = {(4, 2), (10, 2), (4, 12), (10, 12), (7, 5), (7, 9)}
        return _make_state(
            brick, steel,
            (Tank(2, 4, 1, 0), Tank(12, 10, -1, 0)),
            (Base(1, 7), Base(13, 7)),
        )
    raise ValueError(f'Unknown map: {name}. Choose from {MAP_NAMES}')


def spawn_state(name: str, mode: str = 'balanced', seed: int | None = None) -> GameState:
    """Create a fair opening; random mode stays reproducible with --seed."""
    state = get_map(name)
    if mode == 'balanced':
        return state
    if mode != 'random':
        raise ValueError('Spawn mode must be balanced or random')
    rng = Random(seed)
    walls = {(w.x, w.y) for w in state.walls}
    bases = {(b.x, b.y) for b in state.bases}
    blocked = walls | bases

    def options(xrange):
        found = []
        for x in xrange:
            for y in range(2, HEIGHT - 2):
                if (x, y) in blocked:
                    continue
                freedom = sum((x + dx, y + dy) not in blocked
                              and 0 <= x + dx < WIDTH and 0 <= y + dy < HEIGHT
                              for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if freedom >= 2:
                    found.append((x, y))
        return found

    left = options(range(2, 5))
    right = options(range(WIDTH - 5, WIDTH - 2))
    choices = []
    for a in left:
        for b in right:
            if a[1] == b[1] or a[0] == b[0]:
                continue
            if abs(a[0] - b[0]) + abs(a[1] - b[1]) < 8:
                continue
            # Hai phe co khoang cach den Base cua minh gan tuong duong.
            da = abs(a[0] - state.bases[0].x) + abs(a[1] - state.bases[0].y)
            db = abs(b[0] - state.bases[1].x) + abs(b[1] - state.bases[1].y)
            if abs(da - db) > 2:
                continue
            # Khong cho tank dung thang hang/cot voi Base doi phuong.
            if a[0] == state.bases[1].x or a[1] == state.bases[1].y:
                continue
            if b[0] == state.bases[0].x or b[1] == state.bases[0].y:
                continue
            choices.append((a, b))
    if not choices:
        raise ValueError(f'No valid random spawns for {name}')
    (x0, y0), (x1, y1) = rng.choice(choices)
    # HP va huong quay giu nguyen, chi thay toa do spawn.
    return replace(state, tanks=(replace(state.tanks[0], x=x0, y=y0),
                                 replace(state.tanks[1], x=x1, y=y1)))
