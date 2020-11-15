from typing import List, Set, Dict, Tuple, Optional
import random
import players
from characters import all_characters
from deck import Deck
import roles

class Game:
    def __init__(self):
        super().__init__()
        self.players: List[players.Player] = []
        self.deck: Deck = None
        self.started = False
        self.turn = 0

    def add_player(self, player: players.Player):
        player.join_game(self)
        self.players.append(player)
    
    def choose_characters(self):
        char_cards = random.sample(all_characters(), len(self.players))
        for i in range(len(self.players)):
            self.players[i].set_available_character(char_cards[i*2:i*2+2])

    def start_game(self):
        if self.started:
            return
        self.started = True
        self.deck = Deck()
        self.choose_characters()

    def distribute_roles(self):
        available_roles: List[roles.Role] = []
        if len(self.players) == 3:
            available_roles = [roles.Sheriff(), roles.Renegade(), roles.Outlaw()]
        random.shuffle(available_roles)
        for i in range(len(self.players)):
            self.players[i].set_role(available_roles[i])
            if type(available_roles[i]) == roles.Sheriff:
                self.turn = i
            self.players[i].prepare()
            for k in range(self.players[i].max_lives):
                self.players[i].hand.append(self.deck.draw())
        self.play_turn()

    def play_turn(self):
        self.players[self.turn].play_turn()

    def next_turn(self):
        self.turn = (self.turn + 1) % len(self.players)
        self.play_turn()

