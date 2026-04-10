import math
import random


class Node:
    def __init__(self, state, player_to_move, parent=None, move=None):
        self.state = state
        self.player_to_move = player_to_move
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = state.available_moves()

    def is_terminal(self):
        return self.state.is_terminal()

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def expand(self):
        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)

        next_state = self.state.clone()
        next_state.play_move(self.player_to_move, move)
        next_player = next_state.next_player(self.player_to_move)

        child = Node(next_state, next_player, parent=self, move=move)
        self.children.append(child)
        return child

    def best_child(self, exploration_weight=math.sqrt(2)):
        best_score = float("-inf")
        best_node = None

        for child in self.children:
            exploitation = child.wins / child.visits
            exploration = exploration_weight * math.sqrt(
                math.log(self.visits) / child.visits
            )
            score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_node = child

        return best_node

    def best_move_child(self):
        return max(self.children, key=lambda child: child.visits)


class MCTS:
    def __init__(self, iterations=1000):
        self.iterations = iterations

    def search(self, game, player):
        root = Node(game.clone(), player)

        for _ in range(self.iterations):
            node = self._select(root)
            result = self._simulate(node)
            self._backpropagate(node, result, player)

        if not root.children:
            return None

        return root.best_move_child().move

    def _select(self, node):
        current = node

        while not current.is_terminal():
            if not current.is_fully_expanded():
                return current.expand()
            current = current.best_child()

        return current

    def _simulate(self, node):
        rollout_state = node.state.clone()
        current_player = node.player_to_move

        while not rollout_state.is_terminal():
            move = random.choice(rollout_state.available_moves())
            rollout_state.play_move(current_player, move)
            current_player = rollout_state.next_player(current_player)

        return rollout_state.check_winner()

    def _backpropagate(self, node, winner, root_player):
        current = node

        while current is not None:
            current.visits += 1

            if winner == root_player:
                current.wins += 1
            elif winner is None:
                current.wins += 0.5

            current = current.parent
