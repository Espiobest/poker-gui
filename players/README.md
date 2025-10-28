# AI Players

Two versions of the AI player:

## `custom_player_numpy.py` (Production)
Uses NumPy for inference. PyTorch is too large for Vercel's 250MB deployment limit, so we extracted the trained weights to JSON and run inference with NumPy instead.

## `custom_player.py` (Development)
Original PyTorch version. Use this for local development or training new models.

## Using PyTorch Locally

To switch to the PyTorch version:

1. Install PyTorch:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

2. Update `game_logic.py`:
```python
from players.custom_player import CustomPlayer  # instead of custom_player_numpy
```

## Training New Models

After training a new model:
```bash
python extract_weights.py  # Extracts weights from model.pth to model_weights.json
```

Both versions produce identical decisions - verified with automated tests.
