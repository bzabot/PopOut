# MCTS Service

`mcts_service.py` contains a generic Monte Carlo Tree Search implementation.
It is not tied to TicTacToe. It can be reused for another deterministic,
turn-based game as long as the game object implements the contract below.

## Game Contract

The object passed to `MCTS.search(game)` must provide these methods:

```python
game.clone()
game.available_moves()
game.apply_move(move)
game.is_terminal()
game.check_winner()
```

### `clone()`

Returns an independent copy of the current game state.

MCTS modifies cloned states during search, so `clone()` must not return the
same object. If it does, simulations will corrupt the real game.

```python
copy = game.clone()
```

### `available_moves()`

Returns a list of all legal moves for the current state.

The move format is decided by the game. In TicTacToe it is a tuple:

```python
(row, column)
```

For PopOut it could be a custom object, for example:

```python
Move(type="drop", column=3)
```

The only requirement is that `apply_move(move)` knows how to apply the
same move objects returned by `available_moves()`.

### `apply_move(move)`

Applies `move` for the game's current player to the game state and returns the
player who moved.

Inside MCTS this is called only on cloned states. In the real game loop, you
call it after receiving the chosen move:

```python
best_move = mcts.search(game)
game.apply_move(best_move)
```

### `is_terminal()`

Returns `True` when the game is over.

Examples:

- a player has won
- the board is full and the result is a draw
- a game-specific draw rule was reached

### `check_winner()`

Returns the winning player, or `None` if there is no winner.

This implementation treats `None` as a draw during backpropagation, so
`is_terminal()` must distinguish between "game is still running" and "game
ended without a winner".

Correct behavior:

```python
if game.is_terminal():
    winner = game.check_winner()
    # winner is "X", "O", or None for draw
```

## Usage

```python
from src.MCTS.mcts_service import MCTS

game = TicTacToe()
mcts = MCTS(iterations=1000)

current_player = "O"
game.turn = current_player
best_move = mcts.search(game)

if best_move is not None:
    game.apply_move(best_move)
```

## How Moves Are Chosen

Each search iteration has four phases:

1. Selection: walk down the tree using UCT.
2. Expansion: add one unexplored child move.
3. Simulation: play moves until the game ends.
4. Backpropagation: update visit and win statistics.

At the end, the chosen move is the root child with the most visits.

The implementation adds two improvements over the plain random-rollout
baseline:

```python
from src.mcts.mcts_service import MCTS

mcts = MCTS(iterations=1000)
```

Expansion itself stays random, as in the plain MCTS baseline. Selection adds
a small heuristic bias to UCT after children exist. The bias favors immediate
wins, blocks immediate opponent wins, penalizes moves that give the opponent a
direct winning reply, and prefers central columns.

The rollout is tactical but still cheap enough for repeated simulations: it
plays an immediate win if one exists, blocks an existing immediate opponent
win, and otherwise uses a center-biased random move.

## Important Detail About Win Counts

Each node stores wins from the perspective of the player who made the move into
that node. This matters because MCTS must model the opponent as adversarial.

If every node stores wins only from the root player's perspective, then opponent
turns may accidentally select moves that are good for the AI instead of moves
that are good for the opponent.

## Minimal Example Game Skeleton

```python
class MyGame:
    turn = ...

    def clone(self):
        return MyGame(...)

    def available_moves(self):
        return [...]

    def apply_move(self, move):
        ...

    def is_terminal(self):
        ...

    def check_winner(self):
        ...
```
