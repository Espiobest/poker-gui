# Poker Game vs AI Bot

A web-based poker game where you can play against an AI bot trained with Deep Q-Learning.

## Features

- Interactive web UI to play Texas Hold'em poker
- AI opponent powered by a trained DQN model
- Real-time game updates
- Support for Fold, Call, and Raise actions
- Clean and intuitive interface

## Setup Instructions

### 1. Create a Virtual Environment

Using conda:
```bash
conda create -n poker-ui python=3.9
conda activate poker-ui
```

Or using venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: PyPokerEngine is included locally in the `pypokerengine/` directory and does not need to be installed from PyPI.

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 4. Play the Game

1. Open your web browser and navigate to `http://localhost:5000`
2. Click "Start New Game" to begin
3. You'll be dealt two hole cards
4. Choose your action: Fold, Call, or Raise
5. If you raise, enter the amount you want to raise
6. Play continues until the round ends
7. Click "Next Round" to continue playing

## Game Rules

- **Initial Stack**: $1000 per player
- **Small Blind**: $10
- **Max Rounds**: 10 rounds per game
- **Actions**:
  - **Fold**: Give up your hand
  - **Call**: Match the current bet
  - **Raise**: Increase the bet (limited to 4 raises per street)

## Architecture

- **Frontend**: HTML/CSS/JavaScript for the game interface
- **Backend**: Flask server managing game state and AI opponent
- **AI Model**: DQN trained with PyTorch, deployed with NumPy (see [players/README.md](players/README.md))
- **Game Engine**: PyPokerEngine for poker game logic

### Two AI Versions

This project includes **two versions** of the AI player:

1. **`custom_player_numpy.py`** (Production) - Lightweight NumPy-only version for Vercel deployment
2. **`custom_player.py`** (Development) - Full PyTorch version for local development and training

Both produce **identical decisions** (verified with automated tests). See [players/README.md](players/README.md) for details.

## Notes

- The game runs locally on your machine
- Game state is stored in server memory (not persistent)
- The AI uses a 3-feature input: win rate, normalized stack, and normalized pot size
- The model outputs Q-values for 3 actions: Fold, Call, Raise

## Troubleshooting

If you encounter issues:

1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Verify that `models/model_weights.json` exists
3. Check that port 5000 is not in use by another application
4. Try running with `python app.py` instead of `flask run`
5. For AI issues, see [players/README.md](players/README.md)

Enjoy playing poker against the AI!
