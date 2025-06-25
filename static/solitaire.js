let gameState = null;

// Load game state saat halaman dimuat
document.addEventListener('DOMContentLoaded', function() {
    loadGameState();
    setupEventListeners();
});

function setupEventListeners() {
    // Setup drop zones for foundations
    for (let i = 0; i < 4; i++) {
        const foundation = document.querySelector(`[data-foundation="${i}"]`);
        if (foundation) {
            foundation.addEventListener('dragover', allowDrop);
            foundation.addEventListener('drop', drop);
            foundation.addEventListener('dragleave', function(e) {
                e.currentTarget.classList.remove('drag-over');
            });
        }
    }

    // Setup drop zones for tableau
    for (let i = 0; i < 7; i++) {
        const tableau = document.querySelector(`[data-tableau="${i}"]`);
        if (tableau) {
            tableau.addEventListener('dragover', allowDrop);
            tableau.addEventListener('drop', drop);
            tableau.addEventListener('dragleave', function(e) {
                e.currentTarget.classList.remove('drag-over');
            });
        }
    }
}

async function loadGameState() {
    try {
        const response = await fetch('/api/game-state');
        gameState = await response.json();
        renderGame();
    } catch (error) {
        console.error('Error loading game state:', error);
    }
}

async function newGame() {
    try {
        const response = await fetch('/api/new-game', { method: 'POST' });
        gameState = await response.json();
        renderGame();
    } catch (error) {
        console.error('Error starting new game:', error);
    }
}

async function drawCard() {
    try {
        const response = await fetch('/api/draw-card', { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            gameState = data.game_state;
            renderGame();
        }
    } catch (error) {
        console.error('Error drawing card:', error);
    }
}

async function autoMove() {
    try {
        const response = await fetch('/api/auto-move', { method: 'POST' });
        const data = await response.json();
        gameState = data.game_state;
        renderGame();
        
        if (data.moves_made > 0) {
            showMessage(`${data.moves_made} kartu dipindahkan otomatis!`);
        }
    } catch (error) {
        console.error('Error auto moving:', error);
    }
}

function renderGame() {
    if (!gameState) return;

    // Update info
    document.getElementById('score').textContent = gameState.score;
    document.getElementById('moves').textContent = gameState.moves;
    // Hapus info joker dan tombol joker jika ada
    const jokerInfo = document.getElementById('joker-info');
    if (jokerInfo) jokerInfo.remove();
    const jokerBtn = document.getElementById('joker-btn');
    if (jokerBtn) jokerBtn.remove();

    // Render deck
    const deckElement = document.getElementById('deck-cards');
    if (gameState.deck.length > 0) {
        deckElement.innerHTML = `<img src="/static/cards/back-blue.svg" class="card-img" />`;
    } else {
        deckElement.innerHTML = '';
    }

    // Render waste - FIXED: Add drag functionality
    const wasteElement = document.getElementById('waste-cards');
    if (gameState.waste.length > 0) {
        const topCard = gameState.waste[gameState.waste.length - 1];
        if (topCard.face_up) {
            wasteElement.innerHTML = `
                <img src="${getCardImageFile(topCard)}" 
                     class="card-img" 
                     draggable="true" 
                     data-card-id="${topCard.id}" />`;
            
            // Add drag event listener to waste card
            const wasteCard = wasteElement.querySelector('img');
            wasteCard.addEventListener('dragstart', drag);
        } else {
            wasteElement.innerHTML = `<img src="/static/cards/back-blue.svg" class="card-img" />`;
        }
    } else {
        wasteElement.innerHTML = '';
    }

    // Render foundations - FIXED: Make draggable
    for (let i = 0; i < 4; i++) {
        const foundation = document.querySelector(`[data-foundation="${i}"]`);
        const cards = gameState.foundations[i];
        if (cards.length > 0) {
            const topCard = cards[cards.length - 1];
            foundation.innerHTML = `
                <img src="${getCardImageFile(topCard)}" 
                     class="card-img" 
                     draggable="true" 
                     data-card-id="${topCard.id}" />`;
            
            // Add drag event listener to foundation card
            const foundationCard = foundation.querySelector('img');
            foundationCard.addEventListener('dragstart', drag);
        } else {
            const suits = ['♠', '♥', '♦', '♣'];
            foundation.innerHTML = `<div class="empty-foundation">${suits[i]}</div>`;
        }
    }

    // Render tableau
    for (let i = 0; i < 7; i++) {
        const column = document.querySelector(`[data-tableau="${i}"]`);
        const cards = gameState.tableau[i];
        column.innerHTML = '';
        
        cards.forEach((card, index) => {
            const cardDiv = document.createElement('div');
            cardDiv.className = `card ${card.color} ${!card.face_up ? 'face-down' : ''}`;
            cardDiv.style.marginTop = index === 0 ? '0' : '-90px';
            cardDiv.style.position = 'relative';
            cardDiv.style.zIndex = index;
            
            if (card.face_up) {
                cardDiv.setAttribute('draggable', 'true');
                cardDiv.setAttribute('data-card-id', card.id);
                cardDiv.innerHTML = `<img src="${getCardImageFile(card)}" class="card-img" />`;
                cardDiv.addEventListener('dragstart', drag);
            } else {
                cardDiv.innerHTML = `<img src="/static/cards/back-blue.svg" class="card-img" />`;
            }
            
            column.appendChild(cardDiv);
        });
    }

    // Check win condition
    if (gameState.is_won) {
        document.getElementById('finalScore').textContent = gameState.score;
        document.getElementById('winMessage').style.display = 'block';
    }
}

function drag(ev) {
    const cardId = ev.target.dataset.cardId || ev.target.parentElement.dataset.cardId;
    ev.dataTransfer.setData("text", cardId);
    ev.target.classList.add('dragging');
    console.log('Dragging card:', cardId); // Debug log
}

function allowDrop(ev) {
    ev.preventDefault();
    ev.currentTarget.classList.add('drag-over');
}

function drop(ev) {
    ev.preventDefault();
    ev.currentTarget.classList.remove('drag-over');
    
    const cardId = ev.dataTransfer.getData("text");
    const target = ev.currentTarget;
    
    console.log('Dropping card:', cardId, 'on target:', target); // Debug log
    
    let targetType, targetIndex;
    
    if (target.dataset.foundation !== undefined) {
        targetType = 'foundation';
        targetIndex = parseInt(target.dataset.foundation);
    } else if (target.dataset.tableau !== undefined) {
        targetType = 'tableau';
        targetIndex = parseInt(target.dataset.tableau);
    } else {
        console.log('Invalid drop target'); // Debug log
        return;
    }
    
    console.log('Moving to:', targetType, targetIndex); // Debug log
    moveCard(cardId, targetType, targetIndex);
    
    // Remove dragging class
    document.querySelectorAll('.dragging').forEach(el => {
        el.classList.remove('dragging');
    });
}

async function moveCard(cardId, targetType, targetIndex) {
    try {
        console.log('API call - moveCard:', { cardId, targetType, targetIndex }); // Debug log
        
        const response = await fetch('/api/move-card', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                card_id: cardId,
                target_type: targetType,
                target_index: targetIndex
            })
        });
        
        const data = await response.json();
        console.log('API response:', data); // Debug log
        
        if (data.success) {
            gameState = data.game_state;
            renderGame();
            showMessage('Gerakan berhasil!');
        } else {
            showMessage('Gerakan tidak valid!');
        }
    } catch (error) {
        console.error('Error moving card:', error);
        showMessage('Error saat memindahkan kartu!');
    }
}

function showMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 15px;
        border-radius: 5px;
        z-index: 1000;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    `;
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

function getCardImageFile(card) {
    const rankMap = {
        'A': 'ace',
        '2': '2',
        '3': '3',
        '4': '4',
        '5': '5',
        '6': '6',
        '7': '7',
        '8': '8',
        '9': '9',
        '10': '10',
        'J': 'jack',
        'Q': 'queen',
        'K': 'king'
    };
    const suitMap = {
        'spades': 'spades',
        'hearts': 'hearts',
        'diamonds': 'diamonds',
        'clubs': 'clubs'
    };
    return `/static/cards/${rankMap[card.rank]}_of_${suitMap[card.suit]}.svg`;
}