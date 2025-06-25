from flask import Flask, jsonify, request, session, render_template
import random
import uuid
from typing import List, Optional, Dict, Any
from copy import deepcopy

app = Flask(__name__)
app.secret_key = 'solitaire-secret-key-change-in-production'

games = {}

def suit_to_foundation_index(suit):
    mapping = {'spades': 0, 'hearts': 1, 'diamonds': 2, 'clubs': 3}
    return mapping[suit]

class Card:
    SUITS = ['spades', 'hearts', 'diamonds', 'clubs']
    SUIT_SYMBOLS = {'spades': '♠', 'hearts': '♥', 'diamonds': '♦', 'clubs': '♣'}
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
        self.face_up = False
        self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'suit': self.suit,
            'rank': self.rank,
            'face_up': self.face_up,
            'symbol': self.SUIT_SYMBOLS[self.suit],
            'color': 'red' if self.suit in ['hearts', 'diamonds'] else 'black'
        }
    
    def get_value(self) -> int:
        return self.RANKS.index(self.rank) + 1
    
    def is_red(self) -> bool:
        return self.suit in ['hearts', 'diamonds']
    
    def is_black(self) -> bool:
        return self.suit in ['spades', 'clubs']

class SolitaireGame:
    def __init__(self):
        self.deck = []
        self.waste = []
        self.foundations = [[] for _ in range(4)]
        self.tableau = [[] for _ in range(7)]
        self.score = 0
        self.moves = 0
        self.move_history = []  # Tambahkan history untuk undo
        self.create_deck()
        self.setup_game()
    
    def create_deck(self):
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                self.deck.append(Card(suit, rank))
        random.shuffle(self.deck)
    
    def setup_game(self):
        for col in range(7):
            for row in range(col + 1):
                if self.deck:
                    card = self.deck.pop()
                    if row == col:
                        card.face_up = True
                    self.tableau[col].append(card)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'deck': [card.to_dict() for card in self.deck],
            'waste': [card.to_dict() for card in self.waste],
            'foundations': [[card.to_dict() for card in foundation] for foundation in self.foundations],
            'tableau': [[card.to_dict() for card in column] for column in self.tableau],
            'score': self.score,
            'moves': self.moves,
            'is_won': self.is_won()
        }
    
    def draw_from_deck(self) -> bool:
        if self.deck:
            # Simpan state sebelum draw untuk undo
            old_state = self.save_state()
            
            card = self.deck.pop()
            card.face_up = True
            self.waste.append(card)
            self.moves += 1
            
            # Simpan move untuk undo
            self.move_history.append({
                'type': 'draw_card',
                'old_state': old_state
            })
            return True
        elif self.waste:
            # Simpan state sebelum recycle untuk undo
            old_state = self.save_state()
            
            while self.waste:
                card = self.waste.pop()
                card.face_up = False
                self.deck.append(card)
            self.moves += 1
            
            # Simpan move untuk undo
            self.move_history.append({
                'type': 'recycle_deck',
                'old_state': old_state
            })
            return True
        return False
    
    def find_card_by_id(self, card_id: str) -> tuple:
        # Cari di deck
        for i, card in enumerate(self.deck):
            if card.id == card_id:
                return card, ('deck', i)
        
        # Cari di waste
        for i, card in enumerate(self.waste):
            if card.id == card_id:
                return card, ('waste', i)
        
        # Cari di tableau
        for col_idx, column in enumerate(self.tableau):
            for card_idx, card in enumerate(column):
                if card.id == card_id:
                    return card, ('tableau', col_idx, card_idx)
        
        # Cari di foundations
        for found_idx, foundation in enumerate(self.foundations):
            for card_idx, card in enumerate(foundation):
                if card.id == card_id:
                    return card, ('foundation', found_idx, card_idx)
        
        return None, None
    
    def can_move_to_foundation(self, card: Card, foundation_idx: int, from_waste=False) -> bool:
        foundation = self.foundations[foundation_idx]
        if not foundation:
            return card.rank == 'A' and from_waste
        top_card = foundation[-1]
        return (card.suit == top_card.suit and card.get_value() == top_card.get_value() + 1)
    
    def can_move_to_tableau(self, card: Card, tableau_idx: int) -> bool:
        tableau_col = self.tableau[tableau_idx]
        if not tableau_col:
            return card.rank == 'K'
        top_card = tableau_col[-1]
        return (card.get_value() == top_card.get_value() - 1 and
                ((card.is_red() and top_card.is_black()) or
                 (card.is_black() and top_card.is_red())))
    
    def save_state(self):
        return {
            'deck': deepcopy(self.deck),
            'waste': deepcopy(self.waste),
            'foundations': deepcopy(self.foundations),
            'tableau': deepcopy(self.tableau)
        }
    
    def restore_state(self, state):
        self.deck = deepcopy(state['deck'])
        self.waste = deepcopy(state['waste'])
        self.foundations = deepcopy(state['foundations'])
        self.tableau = deepcopy(state['tableau'])
    
    def move_card(self, card_id: str, target_type: str, target_index: int) -> bool:
        card, location = self.find_card_by_id(card_id)
        if not card or not location:
            return False
        old_state = self.save_state()
        from_waste = (location[0] == 'waste')
        if location[0] == 'tableau':
            col_idx, card_idx = location[1], location[2]
            moving_cards = self.tableau[col_idx][card_idx:]
            if not all(c.face_up for c in moving_cards):
                return False
            if not self.can_move_to_tableau(moving_cards[0], target_index):
                return False
            self.tableau[target_index].extend(moving_cards)
            del self.tableau[col_idx][card_idx:]
            self.reveal_tableau_card(col_idx)
            self.moves += 1
            self.score += 5
            self.move_history.append({'type': 'tableau_move','from_col': col_idx,'from_card_idx': card_idx,'to_col': target_index,'cards_moved': len(moving_cards),'old_state': old_state})
            return True
        if not card.face_up:
            return False
        valid_move = False
        if location[0] == 'waste' and location[1] == len(self.waste) - 1:
            valid_move = True
        elif location[0] == 'foundation' and location[2] == len(self.foundations[location[1]]) - 1:
            valid_move = True
        if not valid_move:
            return False
        can_move = False
        if target_type == 'foundation':
            can_move = self.can_move_to_foundation(card, target_index, from_waste=from_waste)
        elif target_type == 'tableau':
            can_move = self.can_move_to_tableau(card, target_index)
        if not can_move:
            return False
        if location[0] == 'waste':
            self.waste.pop()
        elif location[0] == 'foundation':
            self.foundations[location[1]].pop()
        if target_type == 'foundation':
            self.foundations[target_index].append(card)
            self.score += 10
        elif target_type == 'tableau':
            self.tableau[target_index].append(card)
            self.score += 5
        self.moves += 1
        self.move_history.append({'type': 'card_move','from_location': location[0],'from_index': location[1],'from_card_idx': location[2] if location[0] == 'foundation' else None,'to_type': target_type,'to_index': target_index,'old_state': old_state})
        return True
    
    def reveal_tableau_card(self, col_idx: int):
        if self.tableau[col_idx] and not self.tableau[col_idx][-1].face_up:
            self.tableau[col_idx][-1].face_up = True
            self.score += 5
    
    def is_won(self) -> bool:
        return all(len(foundation) == 13 for foundation in self.foundations)
    
    def undo_move(self) -> bool:
        """Undo gerakan terakhir"""
        if not self.move_history:
            return False
        
        last_move = self.move_history.pop()
        self.restore_state(last_move['old_state'])
        return True

def get_game():
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        game_id = str(uuid.uuid4())
        games[game_id] = SolitaireGame()
        session['game_id'] = game_id
    return games[game_id]

def new_game():
    game_id = str(uuid.uuid4())
    games[game_id] = SolitaireGame()
    session['game_id'] = game_id
    return games[game_id]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game-state')
def get_game_state():
    """Mendapatkan state permainan saat ini"""
    game = get_game()
    return jsonify(game.to_dict())

@app.route('/api/new-game', methods=['POST'])
def start_new_game():
    """Memulai permainan baru"""
    game = new_game()
    return jsonify(game.to_dict())

@app.route('/api/draw-card', methods=['POST'])
def draw_card():
    """Mengambil kartu dari deck"""
    game = get_game()
    success = game.draw_from_deck()
    return jsonify({
        'success': success,
        'game_state': game.to_dict()
    })

@app.route('/api/move-card', methods=['POST'])
def move_card():
    """Memindahkan kartu"""
    data = request.get_json()
    game = get_game()
    
    card_id = data.get('card_id')
    target_type = data.get('target_type')  # 'foundation' atau 'tableau'
    target_index = data.get('target_index')
    
    success = game.move_card(card_id, target_type, target_index)
    
    return jsonify({
        'success': success,
        'game_state': game.to_dict()
    })

@app.route('/api/undo', methods=['POST'])
def undo_move():
    """Undo gerakan terakhir"""
    game = get_game()
    success = game.undo_move()
    
    return jsonify({
        'success': success,
        'game_state': game.to_dict()
    })

if __name__ == '__main__':
    app.run(debug=True)