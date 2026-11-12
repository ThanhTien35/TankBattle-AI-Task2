import argparse
import unittest

from benchmarks.compare import run_benchmark
from benchmarks.tournament import run_tournament


def main():
    parser = argparse.ArgumentParser(description="Tank Battle Benchmark")
    group = parser.add_mutually_exclusive_group()

    group.add_argument("--all", action="store_true")
    group.add_argument("--tactical", action="store_true")
    group.add_argument("--tournament", action="store_true")
    group.add_argument("--test", action="store_true")

    parser.add_argument("--depth", type=int, default=None)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--strict-search", action="store_true")

    args = parser.parse_args()

    # UNIT TESTS
    if args.test:
        suite = unittest.defaultTestLoader.discover("tests")
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(0 if result.wasSuccessful() else 1)

    # AI TOURNAMENT
    if args.tournament:
        run_tournament(
            depth=args.depth or 2,
            rounds=2,
            max_plies=80,
            suite="maps",
            strict_search=args.strict_search
        )

    # FULL BENCHMARK
    elif args.all:
        run_benchmark(
            depths=[2, 3, 4],
            repeats=args.repeats,
            suite="maps",
            output="results/benchmark_all.csv",
            strict_search=args.strict_search
        )

    # TACTICAL BENCHMARK
    elif args.tactical:
        run_benchmark(
            depth=args.depth or 3,
            repeats=args.repeats,
            suite="tactical",
            output="results/benchmark_tactical.csv",
            strict_search=args.strict_search
        )

    # QUICK BENCHMARK
    else:
        run_benchmark(
            depth=args.depth or 3,
            repeats=args.repeats,
            suite="maps",
            output="results/benchmark.csv",
            strict_search=args.strict_search
        )


if __name__ == "__main__":
    main()
