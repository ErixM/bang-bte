from typing import List
import bang.roles as r
import bang.players as pl
from bang.cards import Card, Suit, Bang, Mancato
import bang.expansions.fistful_of_cards.card_events as ce

class Fantasma(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Fantasma', number, is_equipment=True)
        self.icon = '👻️' #porta in vita i giocatori morti ma non
    
    def play_card(self, player, against, _with=None):
        if (player.game.check_event(ce.IlGiudice)):
            return False
        if len(player.game.get_dead_players(include_ghosts=False)) > 0:
            player.pending_action = pl.PendingAction.CHOOSE
            player.choose_text = 'choose_fantasma'
            player.available_cards = [{
                'name': p.name,
                'icon': p.role.icon if(player.game.initial_players == 3) else '⭐️' if isinstance(p.role, r.Sheriff) else '🤠',
                'avatar': p.avatar,
                'alt_text': ''.join(['❤️']*p.lives)+''.join(['💀']*(p.max_lives-p.lives)),
                'is_character': True,
                'noDesc': True
            } for p in player.game.get_dead_players(include_ghosts=False)] 
            player.game.deck.scrap(self, True)
            return True
        return False

class Lemat(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Lemat', number, is_equipment=True, is_weapon=True, range=1)
        self.icon = '🔫' # ogni carta può essere usata come bang
        #TODO

class SerpenteASonagli(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'SerpenteASonagli', number, is_equipment=True)
        self.need_target = True
        self.icon = '🐍️' # Ogni turno pesca se il seme picche -1hp
        self.alt_text = "♠️ =💔"

    def play_card(self, player, against, _with=None):
        if (player.game.check_event(ce.IlGiudice)):
            return False
        if against != None:
            self.reset_card()
            player.sio.emit('chat_message', room=player.game.name,
                          data=f'_play_card_against|{player.name}|{self.name}|{against}')
            player.game.get_player_named(against).equipment.append(self)
            player.game.get_player_named(against).notify_self()
            return True
        return False

class Shotgun(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Shotgun', number, is_equipment=True, is_weapon=True, range=1)
        self.icon = '🔫' # Ogni volta che colpisci un giocatore deve scartare una carta
        #TODO

class Taglia(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Taglia', number, is_equipment=True)
        self.need_target = True
        self.icon = '💰' # chiunque colpisca il giocatore con la taglia pesca una carta dal mazzo, si toglie solo con panico, cat balou, dalton
        #TODO

class UltimoGiro(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'UltimoGiro', number)
        self.icon = '🥂'
        # self.desc = 'Recupera 1 vita'
        # self.desc_eng = 'Regain 1 HP'
        self.alt_text = "🍺"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against)
        player.lives = min(player.lives+1, player.max_lives)
        player.notify_self()
        return True

class Tomahawk(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Tomahawk', number, range=2)
        self.icon = '🪓️'
        self.alt_text = "2🔎 💥"
        # "Spara a un giocatore a distanza 2"
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against != None and player.game.can_card_reach(self, player, against):
            super().play_card(player, against=against)
            player.game.attack(player, against, card_name=self.name)
            return True
        return False

class Sventagliata(Bang):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Sventagliata'
        self.icon = '🎏'
        self.alt_text = "💥💥" # spara al target e anche, a uno a distanza 1 dal target
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against != None:
            #TODO
            # super().play_card(player, against=against)
            # player.game.attack(player, against, card_name=self.name)
            return True
        return False

class Salvo(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Salvo', number)
        self.icon = '😇️'
        self.alt_text = "👤😇️" 
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against != None:
            #TODO
            # super().play_card(player, against=against)
            # player.game.attack(player, against, card_name=self.name)
            return True
        return False

class Mira(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Mira', number)
        self.icon = '👌🏻'
        self.alt_text = "💥🃏💔💔" 
        self.need_target = True
        self.need_with = True

    def play_card(self, player, against, _with=None):
        if against != None:
            #TODO
            # super().play_card(player, against=against)
            # player.game.attack(player, against, card_name=self.name)
            return True
        return False

class Bandidos(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Bandidos', number)
        self.icon = '🤠️'
        self.alt_text = "👤🃏🃏/💔" 
    
    def play_card(self, player, against, _with=None):
        #TODO
        # super().play_card(player, against=against)
        # player.game.attack(player, against)
        return True

class Fuga(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Fuga', number)
        self.icon = '🏃🏻'
        self.alt_text = "❌" 
    
    def play_card(self, player, against, _with=None):
        #TODO
        # super().play_card(player, against=against)
        # player.game.attack(player, against)
        return True

class Poker(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Poker', number)
        self.icon = '🃏'
        self.alt_text = "👤🃏 🃏🃏"
    
    def play_card(self, player, against, _with=None):
        #TODO
        # super().play_card(player, against=against)
        # player.game.attack(player, against)
        return True

class RitornoDiFiamma(Mancato):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'RitornoDiFiamma'
        self.icon = '🔥'
        self.alt_text = "😅 | 💥"
    
    def play_card(self, player, against, _with=None):
        return False

    def use_card(self, player):
        player.notify_self()

def get_starting_deck() -> List[Card]:
    cards = [
        Fantasma(Suit.SPADES, 9),
        Fantasma(Suit.SPADES, 10),
        # Lemat(Suit.DIAMONDS, 4),
        SerpenteASonagli(Suit.HEARTS, 7),
        # Shotgun(Suit.SPADES, 'K'),
        # Taglia(Suit.CLUBS, 9),
        UltimoGiro(Suit.DIAMONDS, 8),
        Tomahawk(Suit.DIAMONDS, 'A'),
        # Sventagliata(Suit.SPADES, 2),
        # Salvo(Suit.HEARTS, 5),
        # Bandidos(Suit.DIAMONDS,'Q'), # gli altri  giocatori scelgono se scartare 2 carte o perdere 1 punto vita
        # Fuga(Suit.HEARTS, 3), # evita l'effetto di carte marroni (tipo panico cat balou) di cui sei bersaglio
        # Mira(Suit.CLUBS, 6),
        # Poker(Suit.HEARTS, 'J'), # tutti gli altri scartano 1 carta a scelta, se non ci sono assi allora pesca 2 dal mazzo
        RitornoDiFiamma(Suit.CLUBS, 'Q'), # un mancato che fa bang
    ]
    for c in cards:
        c.expansion_icon = '👻️'
    return cards
