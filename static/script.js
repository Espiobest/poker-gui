let gameState = null;
let waitingForAction = false;
let previousHumanStack = 1000;
let previousAiStack = 1000;

// Card suit symbols
const suits = {
    'H': '♥',
    'D': '♦',
    'C': '♣',
    'S': '♠'
};

function addLog(message) {
    const log = document.getElementById('game-log');
    const entry = document.createElement('div');
    entry.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
}

function animateStackChange(element, type) {
    // Remove any existing animation classes
    element.parentElement.classList.remove('flash-decrease', 'flash-increase');

    // Force reflow to restart animation
    void element.parentElement.offsetWidth;

    // Add the appropriate animation class
    if (type === 'decrease') {
        element.parentElement.classList.add('flash-decrease');
    } else if (type === 'increase') {
        element.parentElement.classList.add('flash-increase');
    }

    // Remove class after animation completes
    setTimeout(() => {
        element.parentElement.classList.remove('flash-decrease', 'flash-increase');
    }, 500);
}

function formatCard(card) {
    if (!card) return '-';
    let rank = card.slice(1);
    const suit = card[0];

    // Replace T with 10
    if (rank === 'T') {
        rank = '10';
    }

    return rank + suits[suit];
}

function getCardColor(card) {
    if (!card) return '';
    const suit = card[0];
    return (suit === 'H' || suit === 'D') ? 'red' : 'black';
}

function updateUI(state) {
    if (!state) return;

    console.log('Updating UI with state:', state);
    gameState = state;

    // Update round and street info
    document.getElementById('round').textContent = state.round_count || 0;
    document.getElementById('street').textContent = state.street || '-';
    document.getElementById('pot').textContent = state.pot || 0;

    // Update player stacks with animation
    if (state.players) {
        const humanStackElement = document.getElementById('human-stack');
        const aiStackElement = document.getElementById('ai-stack');

        const newHumanStack = state.players.human || 1000;
        const newAiStack = state.players.ai || 1000;

        // Animate human stack changes
        if (newHumanStack < previousHumanStack) {
            animateStackChange(humanStackElement, 'decrease');
        } else if (newHumanStack > previousHumanStack) {
            animateStackChange(humanStackElement, 'increase');
        }

        // Animate AI stack changes
        if (newAiStack < previousAiStack) {
            animateStackChange(aiStackElement, 'decrease');
        } else if (newAiStack > previousAiStack) {
            animateStackChange(aiStackElement, 'increase');
        }

        humanStackElement.textContent = newHumanStack;
        aiStackElement.textContent = newAiStack;

        previousHumanStack = newHumanStack;
        previousAiStack = newAiStack;
    }

    // Update current bets
    if (state.current_bets) {
        document.getElementById('human-bet').textContent = state.current_bets.human || 0;
        document.getElementById('ai-bet').textContent = state.current_bets.ai || 0;
    }

    // Update human cards
    if (state.hole_cards && state.hole_cards.length > 0) {
        const humanCardsDiv = document.getElementById('human-cards');
        humanCardsDiv.innerHTML = '';
        state.hole_cards.forEach(card => {
            const cardDiv = document.createElement('div');
            cardDiv.className = `card ${getCardColor(card)}`;
            cardDiv.textContent = formatCard(card);
            humanCardsDiv.appendChild(cardDiv);
        });
    }

    // Update AI cards (only shown at showdown)
    const aiCardsDiv = document.getElementById('ai-cards');
    if (state.ai_cards && state.ai_cards.length > 0) {
        aiCardsDiv.innerHTML = '';
        state.ai_cards.forEach(card => {
            const cardDiv = document.createElement('div');
            cardDiv.className = `card ${getCardColor(card)}`;
            cardDiv.textContent = formatCard(card);
            aiCardsDiv.appendChild(cardDiv);
        });
    } else {
        // Show card backs when cards are hidden
        aiCardsDiv.innerHTML = `
            <div class="card card-back">?</div>
            <div class="card card-back">?</div>
        `;
    }

    // Update community cards
    if (state.community_cards) {
        const communityCardsDiv = document.getElementById('community-cards');
        communityCardsDiv.innerHTML = '';
        for (let i = 0; i < 5; i++) {
            const cardDiv = document.createElement('div');
            if (i < state.community_cards.length) {
                cardDiv.className = `card ${getCardColor(state.community_cards[i])}`;
                cardDiv.textContent = formatCard(state.community_cards[i]);
            } else {
                cardDiv.className = 'card empty';
                cardDiv.textContent = '-';
            }
            communityCardsDiv.appendChild(cardDiv);
        }
    }

    // Update last actions
    if (state.last_actions) {
        document.getElementById('human-action').textContent = state.last_actions.human || '-';
        document.getElementById('ai-action').textContent = state.last_actions.ai || '-';
    }

    // Show/hide action buttons
    if (state.waiting_for_action) {
        enableActionButtons(state.valid_actions);
    } else {
        disableActionButtons();
    }

    // Show round result if available
    if (state.round_result) {
        showRoundResult(state.round_result);
    }

    // Show next round button if round ended (but not if game is finished)
    if (state.round_ended && !state.final_game) {
        document.getElementById('next-round-btn').style.display = 'inline-block';

        // Show winner overlay
        if (state.winner) {
            showWinnerOverlay(state.winner, state.message);
        }

        // Add round result to log
        if (state.message) {
            addLog(`Round ${state.round_count}: ${state.message}`);
        }
    }

    // Handle final game over
    if (state.final_game || state.game_finished) {
        disableActionButtons();
        document.getElementById('next-round-btn').style.display = 'none';
        document.getElementById('start-btn').style.display = 'inline-block';
        document.getElementById('start-btn').textContent = 'Start New Game';

        // Show game over overlay
        if (state.winner) {
            showWinnerOverlay(state.winner, state.message);
        }

        // Add game over to log
        if (state.message) {
            addLog(`GAME OVER: ${state.message}`);
        }
    }

    // Log any message from the state
    if (state.message) {
        console.log('State message:', state.message);
    }
}

function showWinnerOverlay(winner, message) {
    const overlay = document.getElementById('winner-overlay');
    const winnerText = document.getElementById('winner-text');
    const winnerDetails = document.getElementById('winner-details');

    // Clear previous classes
    overlay.className = 'winner-overlay';

    // Set content and styling based on winner
    if (winner === 'human') {
        overlay.classList.add('winner-human');
        winnerText.textContent = 'YOU WIN';
    } else if (winner === 'ai') {
        overlay.classList.add('winner-ai');
        winnerText.textContent = 'AI WINS';
    } else if (winner === 'tie') {
        overlay.classList.add('winner-tie');
        winnerText.textContent = 'TIE';
    }

    winnerDetails.textContent = message;

    // Show overlay
    overlay.style.display = 'block';

    // Hide after 5 seconds
    setTimeout(() => {
        overlay.style.display = 'none';
    }, 5000);
}

function enableActionButtons(validActions) {
    const foldBtn = document.getElementById('fold-btn');
    const callBtn = document.getElementById('call-btn');
    const raiseBtn = document.getElementById('raise-btn');

    foldBtn.disabled = false;
    callBtn.disabled = false;
    raiseBtn.disabled = false;

    // Disable buttons not in valid actions
    const actionTypes = validActions.map(a => a.action);

    foldBtn.disabled = !actionTypes.includes('fold');
    callBtn.disabled = !actionTypes.includes('call');
    raiseBtn.disabled = !actionTypes.includes('raise');

    waitingForAction = true;
}

function disableActionButtons() {
    document.getElementById('fold-btn').disabled = true;
    document.getElementById('call-btn').disabled = true;
    document.getElementById('raise-btn').disabled = true;
    waitingForAction = false;
}

function makeAction(action) {
    if (!waitingForAction) return;

    if (action === 'raise') {
        showRaiseInput();
        return;
    }

    disableActionButtons();

    const actionText = action === 'call' ? 'called' : action === 'fold' ? 'folded' : action;
    addLog(`You ${actionText}`);

    fetch('/action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: action })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addLog('Error: ' + data.error);
            enableActionButtons(gameState.valid_actions);
        } else {
            updateUI(data);
        }
    })
    .catch(error => {
        addLog('Error: ' + error);
        enableActionButtons(gameState.valid_actions);
    });
}

function showRaiseInput() {
    const raiseSection = document.getElementById('raise-input-section');
    raiseSection.style.display = 'block';

    // Set min and max raise amount if available
    if (gameState && gameState.valid_actions) {
        const raiseAction = gameState.valid_actions.find(a => a.action === 'raise');
        if (raiseAction && raiseAction.amount) {
            const minRaise = raiseAction.amount.min || 0;
            const maxRaise = raiseAction.amount.max || gameState.players.human || 1000;

            document.getElementById('raise-amount').min = minRaise;
            document.getElementById('raise-amount').max = maxRaise;
            document.getElementById('raise-amount').value = minRaise;
        }
    }
}

function confirmRaise() {
    const amount = parseInt(document.getElementById('raise-amount').value);

    if (!amount || amount < 0) {
        addLog('Invalid raise amount');
        return;
    }

    hideRaiseInput();
    disableActionButtons();
    addLog(`You raised to $${amount}`);

    fetch('/action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: 'raise',
            amount: amount
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addLog('Error: ' + data.error);
            enableActionButtons(gameState.valid_actions);
        } else {
            updateUI(data);
        }
    })
    .catch(error => {
        addLog('Error: ' + error);
        enableActionButtons(gameState.valid_actions);
    });
}

function cancelRaise() {
    hideRaiseInput();
}

function hideRaiseInput() {
    document.getElementById('raise-input-section').style.display = 'none';
}

function showRoundResult(result) {
    document.getElementById('next-round-btn').style.display = 'inline-block';

    if (result.winners && result.winners.length > 0) {
        const winner = result.winners[0];
        addLog(`Round ended! Winner: ${winner.name} won $${winner.amount}`);
    } else {
        addLog('Round ended!');
    }
}

function startGame() {
    addLog('========================================');
    addLog('NEW GAME STARTED');
    addLog('========================================');
    fetch('/start_game', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Game start response:', data);
        if (data.error) {
            addLog('Error starting game: ' + data.error);
        } else {
            addLog('Round 1: Cards dealt. Good luck!');
            document.getElementById('start-btn').style.display = 'none';
            updateUI(data);
        }
    })
    .catch(error => {
        addLog('Error: ' + error);
        console.error('Start game error:', error);
    });
}

function nextRound() {
    document.getElementById('next-round-btn').style.display = 'none';

    fetch('/next_round', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addLog('Error: ' + data.error);
        } else if (data.game_finished) {
            addLog(data.message);
            showGameResult(data);
        } else {
            addLog(`Round ${data.round_count}: Cards dealt.`);
            updateUI(data);
        }
    })
    .catch(error => {
        addLog('Error: ' + error);
    });
}

function showGameResult(data) {
    const winner = data.winner === 'human' ? 'You' : 'AI Bot';
    addLog(`Game Over! ${winner} won with $${data.final_stacks[data.winner]}!`);
    document.getElementById('start-btn').style.display = 'inline-block';
    document.getElementById('start-btn').textContent = 'Start New Game';
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    addLog('Welcome to Poker vs AI Bot!');
    addLog('Click "Start New Game" to begin.');
});
