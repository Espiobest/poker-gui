from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

from torch import nn
import torch

class DQN(nn.Module):
    def __init__(self, input_size):
        super(DQN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 150),
            nn.ReLU(),
            nn.Linear(150, 64),
            nn.ReLU(),
            nn.Linear(64, 3)
        )

    def forward(self, x):
        return self.net(x)
    
class CustomPlayer(BasePokerPlayer):

  def __init__(self):
        super().__init__()
        self.model = DQN(input_size=3)
        import os
        # Go up one level from players/ to project root, then into models/
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'model.pth')
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()

  def declare_action(self, valid_actions, hole_card, round_state):
      state = self.extract_features(hole_card, round_state)
      state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)

      with torch.no_grad():
          q_values = self.model(state_tensor)
          action_index = torch.argmax(q_values).item()

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