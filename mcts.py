from copy import deepcopy as dc

import numpy as np
import pyspiel
from open_spiel.python import games

from node import Node


class Mcts:

    def __init__(self):
        self.c = 1.41

    def ucb(self, node: Node) -> int:
        if node.visits == 0:
            return np.inf
        return node.value / node.visits + self.c * np.sqrt(
            np.log(node.parent.visits) / node.visits
        )

    def select(self, node: Node) -> Node:
        """
        Select stage of MCTS.
        Go through the game tree, layer by layer.
        Chooses the node with the highest UCB-score at each layer.
        Returns a
        """
        print("select")

        
        highest_ucb = -np.inf
        best_node: Node = None
        current_node = node
        
        print(node)
        while current_node.has_children():
            if current_node.state.is_terminal():
                print(len(current_node.children))
                return current_node
            else:
                print("hei")
            for child in current_node.children:
                current_ucb = self.ucb(child)
                if current_ucb > highest_ucb:
                    highest_ucb = current_ucb
                    best_node = child
            current_node = best_node
        return current_node

    def expand(self, node: Node) -> None:
        print("expand")
        """
        Optional stage in the MCTS algorithm.
        If you select a leaf node, this method will not be run.

        You expand once per node, you expand by adding all possible children to the children list.
        """
        legal_actions = node.state.legal_actions()
        for action in legal_actions:
            new_state = dc(node.state)
            new_state.apply_action(action)
            node.children.append(Node(node, new_state, action))

    def simulate(self, node: Node):
        """
        Simulate random moves until you reach a leaf node (A conclusion of the game)
        """
        print("simulate")
        while not (node.state.is_terminal()):
            action = np.random.choice(node.state.legal_actions())
            node.state.apply_action(action)
        return node.state.returns()

    def backpropagate(self, node: Node, result: int):
        print("backpropagate")
        """
        Return the results all the way back up the game tree.
        """
        node.visits += 1
        if node.parent != None:
            node.value += result
            self.backpropagate(node.parent, -result)

    def run_simulation(self, state, num_simulations=10000):
        """
        Simulate a game to its conclusion.
        Random moves are selected all the way.
        """
        root_node = Node(None, state, None)
        self.expand(root_node)
        for _ in range(num_simulations):
            node = self.select(root_node)  # Get desired childnode
            # print(node)
            # print(node.state)
            if not node.state.is_terminal() and not node.has_children():
                self.expand(node)  # creates all its children
            winner = self.simulate(node)
            winner = winner[root_node.state.current_player()]
            self.backpropagate(node, winner)

        print([node.visits for node in root_node.children])
        return max(
            root_node.children, key=lambda node: node.visits
        ).action  # The best action


if __name__ == "__main__":
    game = pyspiel.load_game("tic_tac_toe")
    state = game.new_initial_state()
    first_state = dc(state)
    mcts = Mcts()
    action = mcts.run_simulation(state)
    print(action)

    # state.apply_action(0)
    # print(state.current_player())
    # #print(state.legal_actions())
    # while not state.is_terminal():
    #     action = np.random.choice(state.legal_actions())
    #     state.apply_action(action)
    #     #print(state.current_player(), "\n")
    # print(first_state)
    # print(state)
    # print(state.returns())


"""
state.returns() -> rewards for the game.
state.apply_action(action) -> Play an action [number from 0 to 9]
"""
