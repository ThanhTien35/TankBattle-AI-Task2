"""Validate an external agent against the same public interface used by the GUI."""
import argparse
from agents.registry import ExternalAgent
from benchmarks.scenarios import get_scenarios
from engine.game import legal_actions


def validate(module: str):
    # Test agent voi nhieu state khac nhau
    agent = ExternalAgent(module)
    for scenario in get_scenarios('all'):
        action = agent.choose_action(scenario.state)
        if action not in legal_actions(scenario.state):
            raise AssertionError(f'Illegal action in {scenario.name}: {action}')
        print(f'{scenario.name:22s} -> {action.value}')
    print('PASS: external agent API validated')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--module', default='external_agents.example_agent')
    args = parser.parse_args()
    validate(args.module)
