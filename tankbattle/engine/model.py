"""Immutable, hashable game model for safe adversarial search."""
from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional

WIDTH, HEIGHT = 15, 15
MAX_TURNS = 160  # Additional safety rule for a demo that cannot run forever.

class Action(str, Enum):
    MOVE_UP = 'MOVE_UP'
    MOVE_DOWN = 'MOVE_DOWN'
    MOVE_LEFT = 'MOVE_LEFT'
    MOVE_RIGHT = 'MOVE_RIGHT'
    FIRE = 'FIRE'
    STAY = 'STAY'

DIRECTIONS = {
    Action.MOVE_UP: (0, -1),
    Action.MOVE_DOWN: (0, 1),
    Action.MOVE_LEFT: (-1, 0),
    Action.MOVE_RIGHT: (1, 0),
}

@dataclass(frozen=True)
class Tank:
    x: int
    y: int
    dx: int
    dy: int
    hp: int = 6

@dataclass(frozen=True)
class Base:
    x: int
    y: int
    hp: int = 9

@dataclass(frozen=True)
class Wall:
    x: int
    y: int
    hp: int = 3
    kind: str = "brick"  # Pixel-art appearance; both types obey the assignment HP=3 rule.

@dataclass(frozen=True)
class Bullet:
    x: int
    y: int
    dx: int
    dy: int
    owner: int

@dataclass(frozen=True)
class GameState:
    tanks: tuple[Tank, Tank]
    bases: tuple[Base, Base]
    walls: tuple[Wall, ...]
    bullets: tuple[Bullet, ...] = ()
    turn: int = 0
    ply: int = 0
    winner: Optional[int] = None  # 0 or 1; -1 is a draw
    reason: str = ''

    @property
    def terminal(self) -> bool:
        return self.winner is not None


def initial_state() -> GameState:
    """Symmetrical Battle City-style map with both brick and steel-looking walls.

    The two wall styles are purely visual: BOTH have HP=3 and take one damage
    per bullet, as required by the assignment. The foliage is non-blocking
    background terrain drawn by the UI, not part of the search state.
    """
    original = {
        (4, 1), (4, 2), (4, 3), (4, 7), (4, 8), (4, 9),
        (10, 1), (10, 2), (10, 3), (10, 7), (10, 8), (10, 9),
        (6, 3), (7, 3), (8, 3), (6, 7), (7, 7), (8, 7), (7, 5),
    }
    left = {
        (1, 1), (2, 1), (3, 1), (5, 1),
        (1, 2), (3, 2), (5, 2),
        (1, 3), (1, 4),
        (1, 7), (1, 8), (1, 9), (2, 9), (3, 9),
        (1, 10), (2, 10), (3, 10), (4, 10),
        (2, 12), (3, 12), (4, 12),
    }
    bottom = {(6, 12), (7, 12), (8, 12), (6, 13), (8, 13), (7, 14)}
    coordinates = original | left | {(WIDTH - 1 - x, y) for x, y in left} | bottom
    steel = {
        (1, 3), (13, 3), (2, 9), (12, 9),
        (6, 3), (7, 3), (8, 3),
        (6, 7), (7, 7), (8, 7), (7, 14),
    }
    return GameState(
        tanks=(Tank(2, 5, 1, 0), Tank(12, 5, -1, 0)),
        bases=(Base(1, 5), Base(13, 5)),
        walls=tuple(Wall(x, y, kind='steel' if (x, y) in steel else 'brick')
                    for x, y in sorted(coordinates, key=lambda xy: (xy[1], xy[0]))),
    )
