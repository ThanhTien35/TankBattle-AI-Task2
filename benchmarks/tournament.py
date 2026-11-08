"""Mirrored, deterministic AI-vs-AI tournament (no PyGame required).

Every pair of algorithms plays each selected starting position in both seat
assignments. Rounds 1 and 2 use opposite first movers, identically for both
seat assignments. Early max-plies cutoffs are recorded as UNFINISHED, NOT draws.
"""
from __future__ import annotations
import argparse
import csv
from collections import defaultdict
from dataclasses import replace
from itertools import combinations
from pathlib import Path
from agents.search import MODES, SearchAgent
from benchmarks.scenarios import Scenario, tournament_scenarios, map_scenarios, get_scenarios
from engine.game import apply_action
from engine.model import Action, GameState


def play_match(start: GameState, modes: tuple[str, str], depth: int,
               max_plies: int, strict_search: bool = False) -> dict:
    state = start
    agents = (SearchAgent(modes[0], depth, gameplay_tactics=not strict_search),
              SearchAgent(modes[1], depth, gameplay_tactics=not strict_search))
    stats = [dict(decisions=0, time_ms=0.0, nodes=0, prunes=0, fires=0,
                  moves=0, stays=0) for _ in (0, 1)]
    for _ in range(max_plies):
        if state.terminal:
            break
        p = state.turn
        action = agents[p].choose_action(state)
        s = agents[p].stats
        rec = stats[p]
        rec['decisions'] += 1
        rec['time_ms'] += s.elapsed_ms
        rec['nodes'] += s.nodes
        rec['prunes'] += s.prunes
        rec['fires'] += action == Action.FIRE
        rec['stays'] += action == Action.STAY
        rec['moves'] += action in (Action.MOVE_UP, Action.MOVE_DOWN,
                                  Action.MOVE_LEFT, Action.MOVE_RIGHT)
        state = apply_action(state, action)
    if state.terminal:
        status = 'draw' if state.winner == -1 else 'win'
        winner_mode = '' if state.winner == -1 else modes[state.winner]
        reason = state.reason
    else:
        status = 'unfinished'
        winner_mode = ''
        reason = f'Benchmark cutoff at {max_plies} plies (NOT a draw)'
    return {
        'p0_algorithm': modes[0], 'p1_algorithm': modes[1],
        'depth': depth, 'max_plies': max_plies,
        'result': status, 'winner_player': state.winner if status == 'win' else '',
        'winner_algorithm': winner_mode,
        'plies_played': state.ply - start.ply,
        'reason': reason,
        'p0_tank_hp': state.tanks[0].hp, 'p1_tank_hp': state.tanks[1].hp,
        'p0_base_hp': state.bases[0].hp, 'p1_base_hp': state.bases[1].hp,
        **{f'p{p}_{key}': round(val, 3) if key == 'time_ms' else val
           for p, rec in enumerate(stats) for key, val in rec.items()},
    }


def summarize(rows: list[dict], modes: list[str]) -> list[dict]:
    total = defaultdict(lambda: dict(games=0, wins=0, losses=0, draws=0,
                                     unfinished=0, decisions=0, nodes=0,
                                     prunes=0, time_ms=0.0))
    for row in rows:
        for p in (0, 1):
            name = row[f'p{p}_algorithm']
            rec = total[name]
            rec['games'] += 1
            status = row['result']
            if status == 'win':
                rec['wins' if row['winner_player'] == p else 'losses'] += 1
            elif status == 'draw':
                rec['draws'] += 1
            else:
                rec['unfinished'] += 1
            for k in ('decisions', 'nodes', 'prunes', 'time_ms'):
                rec[k] += row[f'p{p}_{k}']
    output = []
    for name in modes:
        rec = total[name]
        completed = rec['wins'] + rec['losses'] + rec['draws']
        n = rec['decisions']
        output.append({
            'algorithm': name,
            'games': rec['games'], 'wins': rec['wins'],
            'losses': rec['losses'], 'draws': rec['draws'],
            'unfinished': rec['unfinished'],
            'completed_win_rate_pct': (round(100 * rec['wins'] / completed, 2)
                                       if completed else ''),
            'decisions': n,
            'avg_time_ms_per_decision': round(rec['time_ms'] / n, 3) if n else '',
            'avg_nodes_per_decision': round(rec['nodes'] / n, 2) if n else '',
            'avg_prunes_per_decision': round(rec['prunes'] / n, 2) if n else '',
        })
    return output


def _write_csv(path: str, rows: list[dict]):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f'Saved: {target.resolve()}')


def run_tournament(depth: int = 2, max_plies: int = 60, rounds: int = 2,
                   output: str = 'results/tournament.csv',
                   summary_output: str = 'results/tournament_summary.csv',
                   modes: list[str] | None = None,
                   scenarios: list[Scenario] | None = None, suite: str = 'maps',
                   strict_search: bool = False):
    if not 1 <= depth <= 6:
        raise ValueError('depth must be 1..6')
    if max_plies < 1:
        raise ValueError('max-plies must be >= 1')
    if rounds not in (1, 2):
        raise ValueError('rounds must be 1 or 2 (alternate starting player)')
    selected_modes = list(modes) if modes is not None else list(MODES)
    if len(selected_modes) < 2 or len(set(selected_modes)) != len(selected_modes):
        raise ValueError('Provide at least two distinct algorithms')
    if any(m not in MODES for m in selected_modes):
        raise ValueError(f'Unknown algorithm. Choose from {MODES}')
    selected_scenarios = scenarios if scenarios is not None else (
        map_scenarios() if suite == 'maps' else tournament_scenarios()
        if suite == 'legacy' else get_scenarios(suite)
    )
    if not selected_scenarios:
        raise ValueError('No scenarios selected')
    rows = []
    for a, b in combinations(selected_modes, 2):
        for scenario in selected_scenarios:
            for round_index in range(rounds):
                # Dao vi tri agent tren cung state ban dau
                state = replace(scenario.state, turn=round_index % 2)
                for p0, p1 in ((a, b), (b, a)):
                    row = play_match(state, (p0, p1), depth, max_plies, strict_search=strict_search)
                    row = {'scenario': scenario.name, 'round': round_index + 1,
                           'starting_player': state.turn, **row}
                    rows.append(row)
                    print(f"{scenario.name:12s} r{round_index+1} | "
                          f"{p0:22s} vs {p1:22s} | "
                          f"{row['result']:10s} | "
                          f"winner={row['winner_algorithm'] or '-':22s} | "
                          f"{row['plies_played']:3d} plies")
    summary = summarize(rows, selected_modes)
    _write_csv(output, rows)
    _write_csv(summary_output, summary)
    print('\nSUMMARY (win rate excludes unfinished games):')
    for row in summary:
        pct = row['completed_win_rate_pct']
        print(f"{row['algorithm']:22s} | W={row['wins']:2d} L={row['losses']:2d} "
              f"D={row['draws']:2d} unfinished={row['unfinished']:2d} | "
              f"win%={str(pct):>5s} | "
              f"avg nodes/decision={str(row['avg_nodes_per_decision']):>7s}")
    return rows, summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--depth', type=int, default=2)
    parser.add_argument('--max-plies', type=int, default=60)
    parser.add_argument('--strict-search', action='store_true',
                        help='Disable gameplay tie-breaks and root progress bonus')
    parser.add_argument('--rounds', type=int, choices=(1, 2), default=2)
    parser.add_argument('--suite', choices=('maps', 'legacy', 'classic', 'tactical', 'all'), default='maps')
    parser.add_argument('--modes', nargs='+', choices=MODES,
                        help='Subset of algorithms; quote names with spaces')
    parser.add_argument('--output', default='results/tournament.csv')
    parser.add_argument('--summary-output', default='results/tournament_summary.csv')
    args = parser.parse_args()
    run_tournament(depth=args.depth, max_plies=args.max_plies, rounds=args.rounds,
                   modes=args.modes, output=args.output,
                   summary_output=args.summary_output, suite=args.suite,
                   strict_search=args.strict_search)
