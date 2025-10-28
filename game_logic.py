"""
Poker game logic module
Contains the SimplePokerGame class that handles game state and rules
"""

from pypokerengine.engine.deck import Deck
from pypokerengine.engine.hand_evaluator import HandEvaluator
from custom_player import CustomPlayer


class SimplePokerGame:
    """Simplified poker game that doesn't use the full start_poker flow"""

    def __init__(self):
        self.max_rounds = 10
        self.initial_stack = 1000
        self.small_blind = 10
        self.big_blind = 20

        self.human_name = "You"
        self.ai_name = "AI Bot"

        self.ai_player = CustomPlayer()

        # Game state
        self.current_round = 0
        self.game_finished = False

        # Player stacks
        self.player_stacks = {
            'human': self.initial_stack,
            'ai': self.initial_stack
        }

        # Round state
        self.deck = None
        self.human_cards = []
        self.ai_cards = []
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.human_bet = 0
        self.ai_bet = 0
        self.street = 'preflop'
        self.waiting_for_action = False
        self.is_button = True  # Human is button first

    def start_game(self):
        """Start a new game"""
        self.current_round = 1
        self.game_finished = False
        self.player_stacks = {
            'human': self.initial_stack,
            'ai': self.initial_stack
        }

        # Start first round
        self.start_round()

        return self.get_game_state()

    def start_round(self):
        """Start a new poker round"""
        # Create and shuffle deck
        self.deck = Deck()
        self.deck.shuffle()

        # Post blinds
        if self.is_button:
            # Human is button (small blind)
            self.human_bet = self.small_blind
            self.ai_bet = self.big_blind
            self.player_stacks['human'] -= self.small_blind
            self.player_stacks['ai'] -= self.big_blind
        else:
            # AI is button (small blind)
            self.ai_bet = self.small_blind
            self.human_bet = self.big_blind
            self.player_stacks['ai'] -= self.small_blind
            self.player_stacks['human'] -= self.big_blind

        self.pot = self.human_bet + self.ai_bet
        self.current_bet = self.big_blind

        # Deal hole cards
        self.human_cards = [self.deck.draw_card(), self.deck.draw_card()]
        self.ai_cards = [self.deck.draw_card(), self.deck.draw_card()]
        self.community_cards = []

        self.street = 'preflop'
        self.waiting_for_action = True

    def get_valid_actions(self):
        """Get valid actions for the human player"""
        actions = []

        # Can always fold
        actions.append({'action': 'fold', 'amount': 0})

        # Can call if there's a bet to match
        call_amount = self.ai_bet - self.human_bet
        if call_amount > 0:
            actions.append({'action': 'call', 'amount': call_amount})
        else:
            # Can check if no bet
            actions.append({'action': 'call', 'amount': 0})

        # Can raise
        min_raise = max(self.big_blind, self.current_bet * 2)
        max_raise = min(self.player_stacks['human'], self.player_stacks['ai'])

        if min_raise <= max_raise:
            actions.append({
                'action': 'raise',
                'amount': {'min': min_raise, 'max': max_raise}
            })

        return actions

    def get_game_state(self, show_ai_cards=False):
        """Get current game state"""
        return {
            'round_count': self.current_round,
            'street': self.street,
            'pot': self.pot,
            'players': {
                'human': self.player_stacks['human'],
                'ai': self.player_stacks['ai']
            },
            'current_bets': {
                'human': self.human_bet,
                'ai': self.ai_bet
            },
            'hole_cards': [str(card) for card in self.human_cards],
            'ai_cards': [str(card) for card in self.ai_cards] if show_ai_cards else [],
            'community_cards': [str(card) for card in self.community_cards],
            'valid_actions': self.get_valid_actions() if self.waiting_for_action else [],
            'waiting_for_action': self.waiting_for_action,
            'last_actions': {
                'human': f'Bet ${self.human_bet}' if self.human_bet > 0 else '-',
                'ai': f'Bet ${self.ai_bet}' if self.ai_bet > 0 else '-'
            },
            'round_result': None,
            'game_finished': self.game_finished
        }

    def process_action(self, action, amount=None):
        """Process a player action"""
        if not self.waiting_for_action:
            return {'error': 'Not waiting for action'}

        if action == 'fold':
            # AI wins
            self.player_stacks['ai'] += self.pot
            self.pot = 0

            # Check if human is out of chips
            if self.player_stacks['human'] <= 0:
                return self.end_game('ai', 'You ran out of chips! AI Bot wins the game!')

            return self.end_round('AI Bot won! You folded.', show_ai_cards=True, winner='ai')

        elif action == 'call':
            call_amount = self.ai_bet - self.human_bet

            # Clamp to available stack
            call_amount = min(call_amount, self.player_stacks['human'])

            self.human_bet += call_amount
            self.player_stacks['human'] -= call_amount
            self.pot += call_amount

            # Prevent negative
            if self.player_stacks['human'] < 0:
                self.player_stacks['human'] = 0

            # Move to next street or showdown
            return self.next_street()

        elif action == 'raise':
            if amount is None:
                return {'error': 'Raise amount required'}

            # Validate raise amount - can't raise more than you have
            max_raise = self.player_stacks['human']
            if amount > max_raise:
                return {'error': f'Cannot raise more than your stack (${max_raise})'}

            raise_amount = amount
            self.human_bet += raise_amount
            self.player_stacks['human'] -= raise_amount
            self.pot += raise_amount
            self.current_bet = self.human_bet

            # Prevent negative
            if self.player_stacks['human'] < 0:
                self.player_stacks['human'] = 0

            # AI responds (simplified - always calls for now)
            call_amount = self.human_bet - self.ai_bet
            if call_amount <= self.player_stacks['ai']:
                self.ai_bet += call_amount
                self.player_stacks['ai'] -= call_amount
                self.pot += call_amount
                return self.next_street()
            else:
                # AI folds
                self.player_stacks['human'] += self.pot
                self.pot = 0
                return self.end_round('You won! AI folded.', show_ai_cards=True, winner='human')

        return self.get_game_state()

    def next_street(self):
        """Move to the next betting street"""
        if self.street == 'preflop':
            # Deal flop
            self.community_cards = [self.deck.draw_card(), self.deck.draw_card(), self.deck.draw_card()]
            self.street = 'flop'
            self.human_bet = 0
            self.ai_bet = 0
            self.waiting_for_action = True
            return self.get_game_state()

        elif self.street == 'flop':
            # Deal turn
            self.community_cards.append(self.deck.draw_card())
            self.street = 'turn'
            self.human_bet = 0
            self.ai_bet = 0
            self.waiting_for_action = True
            return self.get_game_state()

        elif self.street == 'turn':
            # Deal river
            self.community_cards.append(self.deck.draw_card())
            self.street = 'river'
            self.human_bet = 0
            self.ai_bet = 0
            self.waiting_for_action = True
            return self.get_game_state()

        elif self.street == 'river':
            # Showdown - evaluate hands
            return self.showdown()

    def get_hand_name(self, hole_cards, community_cards):
        """Get human-readable hand name with details"""
        hand_info = HandEvaluator.gen_hand_rank_info(hole_cards, community_cards)
        strength = hand_info['hand']['strength']

        # Get the high card for tiebreakers
        high_rank = hand_info['hand']['high']

        # Convert rank number to card name
        rank_names = {
            14: 'Ace', 13: 'King', 12: 'Queen', 11: 'Jack',
            10: '10', 9: '9', 8: '8', 7: '7', 6: '6',
            5: '5', 4: '4', 3: '3', 2: '2'
        }
        high_card_name = rank_names.get(high_rank, str(high_rank))

        # Convert to readable names with details
        hand_names = {
            'HIGHCARD': f'High Card ({high_card_name})',
            'ONEPAIR': f'Pair of {self._get_plural_rank(high_rank)}',
            'TWOPAIR': f'Two Pair ({high_card_name} high)',
            'THREECARD': f'Three {self._get_plural_rank(high_rank)}',
            'STRAIGHT': f'Straight ({high_card_name} high)',
            'FLASH': f'Flush ({high_card_name} high)',
            'FULLHOUSE': 'Full House',
            'FOURCARD': f'Four {self._get_plural_rank(high_rank)}',
            'STRAIGHTFLASH': f'Straight Flush ({high_card_name} high)'
        }

        return hand_names.get(strength, strength)

    def _get_plural_rank(self, rank):
        """Convert rank to plural form for hand descriptions"""
        rank_names = {
            14: 'Aces', 13: 'Kings', 12: 'Queens', 11: 'Jacks',
            10: 'Tens', 9: 'Nines', 8: 'Eights', 7: 'Sevens', 6: 'Sixes',
            5: 'Fives', 4: 'Fours', 3: 'Threes', 2: 'Twos'
        }
        return rank_names.get(rank, f'{rank}s')

    def showdown(self):
        """Evaluate hands and determine winner at showdown"""
        # Evaluate both hands - HandEvaluator expects hole cards and community cards separately
        human_score = HandEvaluator.eval_hand(self.human_cards, self.community_cards)
        ai_score = HandEvaluator.eval_hand(self.ai_cards, self.community_cards)

        # Get hand info for detailed comparison
        human_info = HandEvaluator.gen_hand_rank_info(self.human_cards, self.community_cards)
        ai_info = HandEvaluator.gen_hand_rank_info(self.ai_cards, self.community_cards)

        # Check if same hand type
        same_hand_type = human_info['hand']['strength'] == ai_info['hand']['strength']

        # Get appropriate hand names - with details only for tiebreakers
        if same_hand_type:
            # Same hand type - include high card details for tiebreaker
            human_hand_name = self.get_hand_name(self.human_cards, self.community_cards)
            ai_hand_name = self.get_hand_name(self.ai_cards, self.community_cards)
        else:
            # Different hand types - use simple names
            human_hand_name = self.get_simple_hand_name(human_info['hand']['strength'])
            ai_hand_name = self.get_simple_hand_name(ai_info['hand']['strength'])

        # Debug print to check scoring
        print(f"DEBUG - Human: {human_hand_name} (score: {human_score}), AI: {ai_hand_name} (score: {ai_score})")

        # Determine winner (HIGHER score is better in PyPokerEngine)
        if human_score > ai_score:
            winner = 'human'
            message = f'You won with {human_hand_name}! AI had {ai_hand_name}'
        elif ai_score > human_score:
            winner = 'ai'
            message = f'AI Bot won with {ai_hand_name}! You had {human_hand_name}'
        else:
            # Tie - split pot
            self.player_stacks['human'] += self.pot // 2
            self.player_stacks['ai'] += self.pot // 2
            self.pot = 0
            return self.end_round(f'Split pot! Both had {human_hand_name}', show_ai_cards=True, winner='tie')

        # Award pot to winner
        self.player_stacks[winner] += self.pot
        self.pot = 0

        return self.end_round(message, show_ai_cards=True, winner=winner)

    def get_simple_hand_name(self, strength):
        """Get simple hand name without details"""
        hand_names = {
            'HIGHCARD': 'High Card',
            'ONEPAIR': 'One Pair',
            'TWOPAIR': 'Two Pair',
            'THREECARD': 'Three of a Kind',
            'STRAIGHT': 'Straight',
            'FLASH': 'Flush',
            'FULLHOUSE': 'Full House',
            'FOURCARD': 'Four of a Kind',
            'STRAIGHTFLASH': 'Straight Flush'
        }
        return hand_names.get(strength, strength)

    def end_round(self, message, show_ai_cards=False, winner=None):
        """End the current round"""
        self.waiting_for_action = False

        # Check if either player is out of chips
        if self.player_stacks['human'] <= 0:
            return self.end_game('ai', 'You ran out of chips! AI Bot wins the game!')
        elif self.player_stacks['ai'] <= 0:
            return self.end_game('human', 'AI Bot ran out of chips! You win the game!')

        state = self.get_game_state(show_ai_cards=show_ai_cards)
        state['message'] = message
        state['round_ended'] = True
        state['winner'] = winner
        return state

    def end_game(self, winner, message):
        """End the entire game"""
        self.game_finished = True
        self.waiting_for_action = False

        state = self.get_game_state(show_ai_cards=True)
        state['game_finished'] = True
        state['winner'] = winner
        state['message'] = message
        state['final_game'] = True
        return state
