from flask import Flask, render_template, request, jsonify, session
from game_logic import PokerGame
import uuid
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Global game state storage
games = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_game', methods=['POST'])
def start_game():
    # Create new game instance
    game_id = str(uuid.uuid4())
    game = PokerGame()

    # Store in session
    session['game_id'] = game_id
    games[game_id] = game

    # Start the game
    state = game.start_game()
    state['message'] = 'Game started! Cards dealt. Make your move!'

    return jsonify(state)


@app.route('/action', methods=['POST'])
def player_action():
    data = request.json
    action = data.get('action')
    amount = data.get('amount')

    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({'error': 'No active game'}), 400

    game = games[game_id]

    # Process the action
    result = game.process_action(action, amount)

    if 'error' in result:
        return jsonify(result), 400

    if 'message' not in result:
        result['message'] = f'You {action}{"ed" if action != "call" else "ed"}'

    return jsonify(result)


@app.route('/next_round', methods=['POST'])
def next_round():
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({'error': 'No active game'}), 400

    game = games[game_id]
    game.current_round += 1

    if game.current_round >= game.max_rounds:
        game.game_finished = True

        winner = 'human' if game.player_stacks['human'] > game.player_stacks['ai'] else 'ai'

        return jsonify({
            'game_finished': True,
            'winner': winner,
            'final_stacks': game.player_stacks,
            'message': f"Game finished! {'You' if winner == 'human' else 'AI Bot'} won!"
        })

    # Flip button position
    game.is_button = not game.is_button

    # Start new round
    game.start_round()

    state = game.get_game_state()
    state['message'] = f'Starting round {game.current_round}. Cards dealt!'

    return jsonify(state)


@app.route('/game_state', methods=['GET'])
def get_game_state():
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({'error': 'No active game'}), 400

    game = games[game_id]
    state = game.get_game_state()

    return jsonify(state)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
