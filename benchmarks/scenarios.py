"""Reproducible benchmark scenarios. Tactical layouts are controlled test fixtures.

They are NOT additional rules from the assignment. Each fixture uses the same
GameState and apply_joint_actions() as the interactive game and AI.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from tankbattle.engine.model import Base, Bullet, GameState, Tank, Wall, initial_state
from tankbattle.engine.maps import MAP_NAMES, get_map


@dataclass(frozen=True)
class Scenario:
    name: str
    state: GameState
    category: str
    purpose: str


def classic_scenarios() -> list[Scenario]:
    start = get_map('Classic Battlefield')
    open_walls = tuple(w for w in start.walls if (w.x, w.y) != (7, 5))
    close = replace(
        start, walls=open_walls,
        tanks=(replace(start.tanks[0], x=5, y=5),
               replace(start.tanks[1], x=9, y=5)),
    )
    critical = replace(
        close, tanks=(replace(close.tanks[0], hp=2),
                      replace(close.tanks[1], hp=2)), turn=1, ply=18,
    )
    return [
        Scenario('Opening', start, 'classic', 'Standard game opening'),
        Scenario('Open lane', close, 'classic', 'Tanks closer with one wall removed'),
        Scenario('Critical HP', critical, 'classic', 'Both tanks at two HP'),
    ]


def tactical_scenarios() -> list[Scenario]:
    bases = (Base(1, 7), Base(13, 7))
    return [
        Scenario(
            'Incoming bullet',
            GameState(
                tanks=(Tank(5, 5, 1, 0, 1), Tank(12, 5, -1, 0, 6)),
                bases=bases, walls=(),
                bullets=(Bullet(3, 5, 1, 0, 1),),
            ),
            'tactical',
            'Tank 0 has 1 HP; staying or firing loses immediately; dodge required',
        ),
        Scenario(
            'Forced flank',
            GameState(
                tanks=(Tank(5, 5, 0, -1, 6), Tank(7, 5, 0, -1, 1)),
                bases=bases,
                walls=(Wall(7, 4), Wall(7, 6), Wall(8, 5)),
            ),
            'tactical',
            'MOVE_RIGHT sets up a forced win in three cycles',
        ),
        Scenario(
            'Finishing shot',
            GameState(
                tanks=(Tank(5, 5, 1, 0, 6), Tank(7, 5, 0, -1, 1)),
                bases=bases, walls=(),
            ),
            'tactical',
            'FIRE wins immediately',
        ),
        Scenario(
            'Brick barrier',
            GameState(
                tanks=(Tank(4, 5, 1, 0, 6), Tank(8, 5, -1, 0, 2)),
                bases=bases, walls=(Wall(6, 5),),
            ),
            'tactical',
            'A wall blocks the direct shot; compare heuristic movement and ties',
        ),
    ]


def map_scenarios() -> list[Scenario]:
    return [Scenario(name, get_map(name), 'map', 'Independent 15x15 battlefield')
            for name in MAP_NAMES]


def tournament_scenarios() -> list[Scenario]:
    """Balanced starting layouts for mirrored agent-vs-agent games."""
    classic = classic_scenarios()
    duel = Scenario(
        'Open duel',
        GameState(
            tanks=(Tank(4, 7, 1, 0, 2), Tank(10, 7, -1, 0, 2)),
            bases=(Base(1, 7), Base(13, 7)), walls=(),
        ),
        'tournament',
        'Symmetric open arena with two-HP tanks',
    )
    return [classic[0], classic[1], duel]


def get_scenarios(suite: str) -> list[Scenario]:
    if suite == 'classic':
        return classic_scenarios()
    if suite == 'tactical':
        return tactical_scenarios()
    if suite == 'maps':
        return map_scenarios()
    if suite == 'all':
        return classic_scenarios() + tactical_scenarios() + map_scenarios()
    raise ValueError(f'Unknown suite: {suite}')
