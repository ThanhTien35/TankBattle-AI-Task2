"""Three independent, deterministic 15x15 maps for the same game rules."""
from __future__ import annotations
from engine.model import Base, GameState, Tank, Wall, WIDTH, HEIGHT, initial_state

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
        return initial_state()
    if name == 'Open Arena':
        steel = {(6, 2), (8, 2), (6, 12), (8, 12)}
        brick = {(3, 3), (11, 3), (3, 11), (11, 11), (7, 4), (7, 10),
                 (5, 6), (9, 6), (5, 8), (9, 8)}
        return _make_state(
            steel | brick, steel,
            (Tank(3, 7, 1, 0), Tank(11, 7, -1, 0)),
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
            (Tank(2, 7, 1, 0), Tank(12, 7, -1, 0)),
            (Base(1, 7), Base(13, 7)),
        )
    raise ValueError(f'Unknown map: {name}. Choose from {MAP_NAMES}')
