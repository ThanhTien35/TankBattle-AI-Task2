# Task 2 - Submission Checklist

## Requirement 1 - Zero-Sum Game (1.0 point)

- `tankbattle/engine/model.py`: immutable state, players, tank/base/wall/bullet, actions.
- `tankbattle/engine/game.py`: legal actions, transition, collision, terminal state.
- `tankbattle/agents/search.py`: terminal utility, heuristic evaluation, Minimax and Alpha-Beta.
- **Explain** the alternating-turn convention and game-cycle bullet update as a design decision.
- **Clarify** depth-limited terminal-only Minimax is not an exhaustive full-game solver.

## Requirement 2 - Algorithms and experiments (1.5 points)

- Four configurations with same state transition and search depth.
- Gameplay mode adds tactical root action ordering and anti-stall bias; `--strict-search` disables them for unmodified search comparison.
- Alpha-Beta vs Minimax and Heuristic Alpha-Beta vs Heuristic Minimax use identical respective evaluation functions.
- `benchmarks.compare`: search time, nodes, leaves, prunes, chosen action, score.
- `benchmarks.tournament`: mirrored matches, wins, losses, draws, unfinished and average search metrics.
- Run experiments at depths 2/3/4; explain exponential growth and pruning benefits.
- Three independent maps + tactical scenarios.
- Anti-stall tests cover the upward FIRE loop, empty shots, forced finishing shots, and gameplay movement. The tactical scenarios are constructed fixtures, not extra game rules.
- **Do not** claim the heuristic is stronger without measured evidence. Distinguish completed win rate from unfinished matches.

## Requirement 3 - GUI and external agents (0.5 point)

- `tankbattle/ui/pygame_app.py`: PyGame UI, two Tank agents, selectable map, STEP/PLAY/RESET, HP, search metrics.
- Battle Log and Replay show stored states without mutating the current match.
- `external_agents`: import `choose_action(state)`, validate legal Action.
- `run_windows.bat` / `requirements.txt`: Windows Python 3.14 + pygame-ce.
- Test GUI on macOS Ventura Intel i5 if this is the evaluation machine.

## Evidence to capture

1. Game GUI on each of three maps.
2. STEP, damage, terminal win condition and Replay/Battle Log.
3. Benchmark CSV for depths 2, 3, 4 and tactical cases.
4. Tournament summary CSV and interpretation of unfinished games.
5. External agent validator and External-vs-AI match.
6. Unit tests passing.

## Short code comments

Important code paths have brief unaccented comments, for example:

```python
# Dan di tung o, kiem tra va cham ngay sau moi o
# Danh gia trang thai cho AI
# Ghi lai state va su kien de xem replay
```
