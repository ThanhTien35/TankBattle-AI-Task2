# AI Behavior Fix - Task 2

## Problem reproduced

At PLY 44 in the earlier Classic Battlefield match, both Tanks were at
(2,4) and (12,4), facing UP with 1 HP. The old terminal-only Minimax and
Alpha-Beta chose FIRE repeatedly, because all nonterminal cutoff states were
scored 0 and FIRE was first in the action list.

## Fix

- `agents/search.py`: inspect first shot impact, distinguish useful hits and
  wall clearing from wasted FIRE; BFS distance to firing lane; incoming bullet
  risk; recent-pose penalty; root tactical ordering and heuristic progress bias.
- Keep `engine/game.py` unchanged: bullets still advance up to three cells per
  cycle, collisions are checked cell by cell, and HP rules are unchanged.
- `--strict-search`: disable gameplay extras when measuring pure search behavior.
- `tests/test_ai_behavior.py`: prevent the same idle-FIRE regression and check
  Minimax/Alpha-Beta parity across maps and sampled game states.

## Validation

- The reconstructed PLY-44 position now produces MOVE_DOWN in Minimax and
  Alpha-Beta instead of FIRE (default gameplay policy).
- Minimax and Alpha-Beta return matching search values and selected actions in
  the automated parity tests.
- Both Tank pairs move and reach terminal outcomes in the sampled 3-map
  depth-3 headless simulations. This does not guarantee every possible game
  terminates before the configured draw limit.
- The current regression suite passed 36/36 tests in the project-building environment.
- The 72-match, 3-map depth-2 tournament with an 80-ply cutoff completed all 72 matches in that environment; results on other configurations may differ.
- The actual PyGame window still needs a check on Windows (pygame-ce was not installed in the project-building environment).
- All tests are runnable with `python -m unittest discover -s tests -v`.

## Academic note

Gameplay action ordering does not change terminal utilities or game rules.
Heuristic root progress bonus is an additional action-selection policy, so
results from default gameplay and `--strict-search` must be reported separately.
