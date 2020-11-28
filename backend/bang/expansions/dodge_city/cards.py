from bang.cards import *

class Binocolo(Mirino):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Binocolo'
        self.icon = '🔍'

class Riparo(Mustang):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Riparo'
        self.icon = '⛰'

class Pugno(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Pugno!', number, range=1)
        self.icon = '👊'
        self.desc = "Spara a un giocatore a distanza 1"
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against != None:
            super().play_card(player, against=against)
            player.game.attack(player, against)
            return True
        return False

class Schivata(Mancato):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Schivata'
        self.icon = '🙅‍♂️'
        self.desc = "Usa questa carta per annullare un Bang! e poi pesca una carta"
        self.alt_text = '☝️🆓'

    def play_card(self, player, against, _with=None):
        return False

    def use_card(self, player):
        player.hand.append(player.game.deck.draw())
        player.notify_self()

class RagTime(Panico):
    def __init__(self, suit, number):
        Card.__init__(self, suit, 'Rag Time', number)
        self.icon = '🎹'
        self.desc = "Ruba 1 carta dalla mano di un giocatore a prescindere dalla distanza"
        self.need_target = True
        self.need_with = True
        self.alt_text = '2🃏'

    def play_card(self, player, against, _with):
        if against != None and _with != None:
            player.game.deck.scrap(_with)
            super().play_card(player, against=against)
            return True
        return False

class Rissa(CatBalou):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Rissa'
        self.icon = '🥊'
        self.desc = "Fai scartare una carta a tutti gli altri giocatori, scegli a caso dalla mano, oppure fra quelle che hanno in gioco"
        self.need_with = True
        self.need_target = False
        self.alt_text = '2🃏'

    def play_card(self, player, against, _with):
        if _with != None:
            player.game.deck.scrap(_with)
            player.event_type = 'rissa'
            super().play_card(player, against=[p.name for p in player.game.players if p != player and (len(p.hand)+len(p.equipment)) > 0][0])
            player.sio.emit('chat_message', room=player.game.name, data=f'{player.name} ha giocato {self.name}')
            return True
        return False

class SpringField(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Springfield', number)
        self.icon = '🌵'
        self.desc = "Spara a un giocatore a prescindere dalla distanza"
        self.need_target = True
        self.need_with = True
        self.alt_text = '2🃏'

    def play_card(self, player, against, _with=None):
        if against != None and _with != None:
            player.game.deck.scrap(_with)
            super().play_card(player, against=against)
            player.game.attack(player, against)
            return True
        return False

class Tequila(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Tequila', number)
        self.icon = '🍹'
        self.desc = "Fai recuperare 1 vita a un giocatore a tua scelta, anche te stesso"
        self.need_target = True
        self.can_target_self = True
        self.need_with = True
        self.alt_text = '2🃏'

    def play_card(self, player, against, _with=None):
        if against != None and _with != None:
            beneficiario = f'{against}' if against != player.name else 'se stesso'
            player.sio.emit('chat_message', room=player.game.name, data=f'{player.name} ha giocato {self.name} per {beneficiario}')
            player.game.deck.scrap(_with)
            player.game.get_player_named(against).lives = min(player.game.get_player_named(against).lives+1, player.game.get_player_named(against).max_lives)
            player.game.get_player_named(against).notify_self()
            return True
        return False

class Whisky(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Whisky', number)
        self.icon = '🥃'
        self.desc = "Gioca questa carta per recuperare fino a 2 punti vita"
        self.need_with = True
        self.alt_text = '2🃏'

    def play_card(self, player, against, _with=None):
        if _with != None:
            super().play_card(player, against=against)
            player.game.deck.scrap(_with)
            player.lives = min(player.lives+2, player.max_lives)
            player.notify_self()
            return True
        return False

class Bibbia(Schivata):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Bibbia'
        self.icon = '📖'
        self.usable_next_turn = True
        self.can_be_used_now = False

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            pass
            return False
        else:
            player.equipment.append(self)
            return True

    def use_card(self, player):
        player.hand.append(player.game.deck.draw())
        player.notify_self()

class Cappello(Mancato):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Cappello'
        self.icon = '🧢'
        self.usable_next_turn = True
        self.can_be_used_now = False

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            pass
            return False
        else:
            player.equipment.append(self)
            return True

class PlaccaDiFerro(Cappello):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Placca Di Ferro'
        self.icon = '🛡'

class Sombrero(Cappello):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Sombrero'
        self.icon = '👒'

def get_starting_deck() -> List[Card]:
    return [
        #TODO: aggiungere anche le carte normalmente presenti https://bang.dvgiochi.com/cardslist.php?id=3
        Barile(Suit.CLUBS, 'A'),
        Binocolo(Suit.DIAMONDS, 10),
        Dinamite(Suit.CLUBS, 10),
        Mustang(Suit.HEARTS, 5),
        Remington(Suit.DIAMONDS, 6),
        RevCarabine(Suit.SPADES, 5),
        Riparo(Suit.DIAMONDS, 'K'),
        Bang(Suit.SPADES, 8),
        Bang(Suit.CLUBS, 5),
        Bang(Suit.CLUBS, 6),
        Bang(Suit.CLUBS, 'K'),
        Birra(Suit.HEARTS, 6),
        Birra(Suit.SPADES, 6),
        CatBalou(Suit.CLUBS, 8),
        Emporio(Suit.SPADES, 'A'),
        Indiani(Suit.DIAMONDS, 5),
        Mancato(Suit.DIAMONDS, 8),
        Panico(Suit.HEARTS, 'J'),
        Pugno(Suit.SPADES, 10),
        RagTime(Suit.HEARTS, 9),
        Rissa(Suit.SPADES, 'J'),
        Schivata(Suit.DIAMONDS, 7),
        Schivata(Suit.HEARTS, 'K'),
        SpringField(Suit.SPADES, 'K'),
        Tequila(Suit.CLUBS, 9),
        Whisky(Suit.HEARTS, 'Q'),
        Bibbia(Suit.HEARTS, 10),
        Cappello(Suit.DIAMONDS, 'J'),
        PlaccaDiFerro(Suit.DIAMONDS, 'A'),
        PlaccaDiFerro(Suit.SPADES, 'Q'),
        Sombrero(Suit.CLUBS, 7),

    ]
