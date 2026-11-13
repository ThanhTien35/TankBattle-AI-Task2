import argparse
from benchmarks.compare import run_benchmark
from benchmarks.tournament import run_tournament
import unittest

def main():
    parser = argparse.ArgumentParser(description='Simultaneous Tank Battle experiments')
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--all', action='store_true')
    g.add_argument('--tactical', action='store_true')
    g.add_argument('--tournament', action='store_true')
    g.add_argument('--test', action='store_true')
    parser.add_argument('--depth', type=int, default=None)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--strict-search', action='store_true')
    args = parser.parse_args()
    if args.test:
        suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(0 if result.wasSuccessful() else 1)
    if args.tournament:
        return run_tournament(depth=args.depth or 1, max_plies=50, rounds=2,
                              strict_search=args.strict_search)
    return run_benchmark(depth=args.depth or 2, depths=[1, 2, 3] if args.all else None,
                         suite='tactical' if args.tactical else 'maps',
                         output=('results/benchmark_all.csv' if args.all else
                                 'results/benchmark_tactical.csv' if args.tactical else 'results/benchmark.csv'),
                         repeats=args.repeats, strict_search=args.strict_search)

if __name__ == '__main__':
    main()
