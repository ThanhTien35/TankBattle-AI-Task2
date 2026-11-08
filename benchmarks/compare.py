"""Reproducible four-mode search benchmark from identical states and depths.

The benchmark measures ONE decision per run, not full games. Repeated calls
measure timing variation, not independent tactical scenarios.
"""
import argparse
import csv
from pathlib import Path
from statistics import mean
from agents.search import MODES, SearchAgent
from benchmarks.scenarios import get_scenarios


def scenarios():
    """Backwards-compatible legacy list of (name, state) pairs."""
    return [(s.name, s.state) for s in get_scenarios('classic')]


def run_benchmark(depth=3, repeats=3, output='results/benchmark.csv',
                  suite='all', depths=None, strict_search=False):
    if repeats < 1:
        raise ValueError('repeats must be >= 1')
    selected_depths = depths if depths is not None else [depth]
    if any(not 1 <= d <= 6 for d in selected_depths):
        raise ValueError('depth must be in 1..6')
    rows = []
    for d in selected_depths:
        for scenario in get_scenarios(suite):
            for mode in MODES:
                samples = []
                for _ in range(repeats):
                    agent = SearchAgent(mode, d, gameplay_tactics=not strict_search)
                    action = agent.choose_action(scenario.state)
                    samples.append((agent.stats, action.value))
                actions = {action for _, action in samples}
                row = {
                    'scenario': scenario.name,
                    'category': scenario.category,
                    'purpose': scenario.purpose,
                    'algorithm': mode,
                    'depth': d,
                    'repeats': repeats,
                    'avg_time_ms': round(mean(s.elapsed_ms for s, _ in samples), 3),
                    'avg_nodes': round(mean(s.nodes for s, _ in samples), 2),
                    'avg_leaves': round(mean(s.leaves for s, _ in samples), 2),
                    'avg_prunes': round(mean(s.prunes for s, _ in samples), 2),
                    'chosen_action': samples[0][1],
                    'consistent_action': len(actions) == 1,
                    'root_score': samples[0][0].score,
                }
                rows.append(row)
                print(f"d={d} | {scenario.name:16s} | {mode:22s} | "
                      f"{row['avg_time_ms']:8.3f} ms | {row['avg_nodes']:6.0f} nodes | "
                      f"{row['avg_prunes']:4.0f} prunes | {row['chosen_action']}")
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    non_fire = sum(row['chosen_action'] != 'FIRE' for row in rows)
    print(f'\nNon-FIRE decisions: {non_fire}/{len(rows)}')
    print(f'Saved: {path.resolve()}')
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--depth', type=int, default=3)
    group.add_argument('--depths', type=int, nargs='+',
                       help='Run multiple depths in one CSV, e.g. --depths 2 3 4')
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--suite', choices=('classic', 'tactical', 'maps', 'all'), default='all')
    parser.add_argument('--output', default='results/benchmark.csv')
    parser.add_argument('--strict-search', action='store_true',
                        help='Measure pure search without gameplay root tie-breaks')
    args = parser.parse_args()
    run_benchmark(depth=args.depth, repeats=args.repeats, output=args.output,
                  suite=args.suite, depths=args.depths,
                  strict_search=args.strict_search)
