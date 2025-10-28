"""
NumPy-only AI player for deployment
Uses extracted weights from the trained DQN model
"""
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import numpy as np
import json
import os

class CustomPlayer(BasePokerPlayer):

    def __init__(self):
        super().__init__()
        # Load weights from JSON
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'model_weights.json')
        with open(model_path, 'r') as f:
            self.weights = json.load(f)

        # Convert lists back to numpy arrays
        self.w1 = np.array(self.weights['layer0_weight'])
        self.b1 = np.array(self.weights['layer0_bias'])
        self.w2 = np.array(self.weights['layer1_weight'])
        self.b2 = np.array(self.weights['layer1_bias'])
        self.w3 = np.array(self.weights['layer2_weight'])
        self.b3 = np.array(self.weights['layer2_bias'])

    def forward(self, x):
        """Forward pass through the neural network"""
        # Layer 1: Linear + ReLU
        x = np.dot(self.w1, x) + self.b1
        x = np.maximum(0, x)  # ReLU

        # Layer 2: Linear + ReLU
        x = np.dot(self.w2, x) + self.b2
        x = np.maximum(0, x)  # ReLU

        # Layer 3: Linear (output)
        x = np.dot(self.w3, x) + self.b3

        return x

    def declare_action(self, valid_actions, hole_card, round_state):
        # Extract features
        state = self.extract_features(hole_card, round_state)
        state_array = np.array(state, dtype=np.float32)

        # Run forward pass
        q_values = self.forward(state_array)
        action_index = np.argmax(q_values)

        # Clip index to valid range to avoid crash
        action_index = min(action_index, len(valid_actions) - 1)
        return valid_actions[action_index]['action']

    def extract_features(self, hole_card, round_state):
        community_card = round_state['community_card']
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=1000,
            nb_player=2,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        my_stack = next(player['stack'] for player in round_state['seats']
                        if player['uuid'] == self.uuid)
        starting_stack = self.starting_stack if hasattr(self, 'starting_stack') else 1000
        norm_stack = my_stack / starting_stack

        pot_size = round_state['pot']['main']['amount']
        norm_pot = pot_size / starting_stack

        return [win_rate, norm_stack, norm_pot]

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
    return CustomPlayer()
