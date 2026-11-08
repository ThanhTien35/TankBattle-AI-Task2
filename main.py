"""Launch PyGame or run a text-only match for CI/headless verification."""
import argparse
from engine.model import initial_state
from engine.maps import MAP_NAMES, get_map
from engine.game import apply_action
from agents.search import SearchAgent
from agents.registry import ExternalAgent
from benchmarks.scenarios import get_scenarios, tournament_scenarios


def available_scenarios():
    return {s.name: s.state for s in get_scenarios('all') + tournament_scenarios()}


def make_agent(name, depth, module, gameplay_tactics=True):
    return (ExternalAgent(module) if name == 'External'
            else SearchAgent(name, depth, gameplay_tactics=gameplay_tactics))


def headless_match(p0, p1, depth, module, max_steps=60, start_state=None,
                   gameplay_tactics=True):
    if 'Human' in (p0, p1):
        raise ValueError('Headless mode does not support Human agents')
    modules = module if isinstance(module, tuple) else (module, module)
    agents = [make_agent(p0, depth, modules[0], gameplay_tactics),
              make_agent(p1, depth, modules[1], gameplay_tactics)]
    state = start_state if start_state is not None else initial_state()
    for _ in range(max_steps):
        player = state.turn
        action = agents[player].choose_action(state)
        state = apply_action(state, action)
        print(f'Ply {state.ply:03d} | P{player + 1} {action.value:<10} | HP {state.tanks[0].hp}-{state.tanks[1].hp} | Base {state.bases[0].hp}-{state.bases[1].hp}')
        if state.terminal:
            break
    print(f'RESULT: winner={state.winner}, reason={state.reason or "step limit reached"}')
    return state


def main():
    parser = argparse.ArgumentParser(description='Task 2 - Tank Battle / Adversarial Search')
    parser.add_argument('--depth', type=int, default=3)
    parser.add_argument('--strict-search', action='store_true',
                        help='Disable gameplay tie-breaks for pure search experiments')
    parser.add_argument('--p0', default='Heuristic Alpha-Beta')
    parser.add_argument('--p1', default='Heuristic Minimax')
    parser.add_argument('--external-module', default='external_agents.example_agent')
    parser.add_argument('--external-p0', help='External module for P1')
    parser.add_argument('--external-p1', help='External module for P2')
    parser.add_argument('--headless', action='store_true', help='Run without PyGame')
    parser.add_argument('--max-steps', type=int, default=60)
    parser.add_argument('--map', choices=MAP_NAMES, help='Choose one of the three main maps')
    parser.add_argument('--scenario', choices=list(available_scenarios()), default='Opening',
                        help='Initial state for GUI or headless demonstration')
    args = parser.parse_args()
    external_modules = (args.external_p0 or args.external_module,
                        args.external_p1 or args.external_module)
    start_state = get_map(args.map) if args.map else available_scenarios()[args.scenario]
    selected_name = args.map or args.scenario
    if args.headless:
        headless_match(args.p0, args.p1, args.depth, external_modules,
                       args.max_steps, start_state=start_state,
                       gameplay_tactics=not args.strict_search)
    else:
        try:
            from ui.pygame_app import run_app
        except ModuleNotFoundError as e:
            if e.name == 'pygame':
                raise SystemExit('PyGame is missing. Install with: python -m pip install -r requirements.txt') from e
            raise
        run_app(args.depth, args.p0, args.p1, external_modules,
                starting_state=start_state, scenario_name=selected_name,
                gameplay_tactics=not args.strict_search)


if __name__ == '__main__':
    main()
