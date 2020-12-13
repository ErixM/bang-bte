
from typing import List, Set, Dict, Tuple, Optional
import random
import socketio
import bang.players as players
import bang.characters as characters
from bang.deck import Deck
import bang.roles as roles
import eventlet

class Game:
    def __init__(self, name, sio:socketio):
        super().__init__()
        self.sio = sio
        self.name = name
        self.players: List[players.Player] = []
        self.dead_players: List[players.Player] = []
        self.deck: Deck = None
        self.started = False
        self.turn = 0
        self.readyCount = 0
        self.waiting_for = 0
        self.initial_players = 0
        self.password = ''
        self.expansions = []
        self.shutting_down = False
        self.is_competitive = False
        self.disconnect_bot = True

    def notify_room(self, sid=None):
        if len([p for p in self.players if p.character == None]) != 0 or sid:
            self.sio.emit('room', room=self.name if not sid else sid, data={
                'name': self.name,
                'started': self.started,
                'players': [{'name':p.name, 'ready': p.character != None} for p in self.players],
                'password': self.password,
                'is_competitive': self.is_competitive,
                'disconnect_bot': self.disconnect_bot,
                'expansions': self.expansions,
            })

    def toggle_expansion(self, expansion_name):
        if not self.started:
            print('toggling', expansion_name)
            if expansion_name in self.expansions:
                self.expansions.remove(expansion_name)
            else:
                self.expansions.append(expansion_name)
            self.notify_room()

    def toggle_competitive(self):
        self.is_competitive = not self.is_competitive
        self.notify_room()

    def toggle_disconnect_bot(self):
        self.disconnect_bot = not self.disconnect_bot
        self.notify_room()

    def add_player(self, player: players.Player):
        if player.is_bot and len(self.players) >= 8:
            return
        if player in self.players or len(self.players) >= 10:
            return
        if len(self.players) > 7:
            if 'dodge_city' not in self.expansions:
                self.expansions.append('dodge_city')
        player.join_game(self)
        self.players.append(player)
        print(f'Added player {player.name} to game')
        self.notify_room()
        self.sio.emit('chat_message', room=self.name, data=f'_joined|{player.name}')

    def set_private(self):
        if self.password == '':
            self.password = ''.join(random.choice("AEIOUJKZT123456789") for x in range(6))
            print(self.name, 'is now private pwd', self.password)
        else:
            self.password = ''
        self.notify_room()

    def notify_character_selection(self):
        self.notify_room()
        if len([p for p in self.players if p.character == None]) == 0:
            for i in range(len(self.players)):
                print(self.name)
                print(self.players[i].name)
                print(self.players[i].character)
                self.sio.emit('chat_message', room=self.name, data=f'_choose_character|{self.players[i].name}|{self.players[i].character.name}|{self.players[i].character.desc}')
                self.players[i].prepare()
                for k in range(self.players[i].max_lives):
                    self.players[i].hand.append(self.deck.draw())
                self.players[i].notify_self()
            self.players[self.turn].play_turn()

    def choose_characters(self):
        char_cards = random.sample(characters.all_characters(self.expansions), len(self.players)*2)
        for i in range(len(self.players)):
            self.players[i].set_available_character(char_cards[i * 2 : i * 2 + 2])

    def start_game(self):
        print('GAME IS STARING')
        if self.started:
            return
        self.players_map = {c.name: i for i, c in enumerate(self.players)}
        self.sio.emit('chat_message', room=self.name, data=f'_starting')
        self.sio.emit('start', room=self.name)
        self.started = True
        self.deck = Deck(self)
        self.initial_players = len(self.players)
        self.distribute_roles()
        self.choose_characters()

    def distribute_roles(self):
        available_roles: List[roles.Role] = []
        if len(self.players) == 3:
            available_roles = [
                roles.Vice('Elimina il Rinnegato 🦅, se non lo elimini tu elimina anche il Fuorilegge'),
                roles.Renegade('Elimina il Fuorilegge 🐺, se non lo elimini tu elimina anche il Vice'),
                roles.Outlaw('Elimina il Vice 🎖, se non lo elimini tu elimina anche il Rinnegato')
            ]
        elif len(self.players) >= 4:
            available_roles = [roles.Sheriff(), roles.Renegade(), roles.Outlaw(), roles.Outlaw(), roles.Vice(), roles.Outlaw(), roles.Vice(), roles.Renegade(), roles.Outlaw(), roles.Vice(), roles.Outlaw()]
            available_roles = available_roles[:len(self.players)]
        random.shuffle(available_roles)
        for i in range(len(self.players)):
            self.players[i].set_role(available_roles[i])
            if isinstance(available_roles[i], roles.Sheriff) or (len(available_roles) == 3 and isinstance(available_roles[i], roles.Vice)):
                if isinstance(available_roles[i], roles.Sheriff):
                    self.sio.emit('chat_message', room=self.name, data=f'_sheriff|{self.players[i].name}')
                self.turn = i
            self.players[i].notify_self()

    def attack_others(self, attacker: players.Player):
        attacker.pending_action = players.PendingAction.WAIT
        attacker.notify_self()
        self.waiting_for = 0
        self.readyCount = 0
        for p in self.players:
            if p != attacker:
                if p.get_banged(attacker=attacker):
                    self.waiting_for += 1
                    p.notify_self()
        if self.waiting_for == 0:
            attacker.pending_action = players.PendingAction.PLAY
            attacker.notify_self()

    def indian_others(self, attacker: players.Player):
        attacker.pending_action = players.PendingAction.WAIT
        attacker.notify_self()
        self.waiting_for = 0
        self.readyCount = 0
        for p in self.players:
            if p != attacker:
                if p.get_indians(attacker=attacker):
                    self.waiting_for += 1
                    p.notify_self()
        if self.waiting_for == 0:
            attacker.pending_action = players.PendingAction.PLAY
            attacker.notify_self()

    def attack(self, attacker: players.Player, target_username:str, double:bool=False):
        if self.get_player_named(target_username).get_banged(attacker=attacker, double=double):
            self.readyCount = 0
            self.waiting_for = 1
            attacker.pending_action = players.PendingAction.WAIT
            attacker.notify_self()
            self.get_player_named(target_username).notify_self()

    def duel(self, attacker: players.Player, target_username:str):
        if self.get_player_named(target_username).get_dueled(attacker=attacker):
            self.readyCount = 0
            self.waiting_for = 1
            attacker.pending_action = players.PendingAction.WAIT
            attacker.notify_self()
            self.get_player_named(target_username).notify_self()

    def emporio(self):
        self.available_cards = [self.deck.draw() for i in range(len(self.players))]
        self.players[self.turn].pending_action = players.PendingAction.CHOOSE
        self.players[self.turn].available_cards = self.available_cards
        self.players[self.turn].notify_self()

    def respond_emporio(self, player, i):
        player.hand.append(self.available_cards.pop(i))
        player.available_cards = []
        player.pending_action = players.PendingAction.WAIT
        player.notify_self()
        nextPlayer = self.players[(self.turn + (len(self.players)-len(self.available_cards))) % len(self.players)]
        if nextPlayer == self.players[self.turn]:
            self.players[self.turn].pending_action = players.PendingAction.PLAY
            self.players[self.turn].notify_self()
        else:
            nextPlayer.pending_action = players.PendingAction.CHOOSE
            nextPlayer.available_cards = self.available_cards
            nextPlayer.notify_self()

    def get_player_named(self, name:str):
        return self.players[self.players_map[name]]

    def responders_did_respond_resume_turn(self):
        self.readyCount += 1
        if self.readyCount == self.waiting_for:
            self.waiting_for = 0
            self.readyCount = 0
            self.players[self.turn].pending_action = players.PendingAction.PLAY
            self.players[self.turn].notify_self()

    def next_player(self):
        return self.players[(self.turn + 1) % len(self.players)]

    def play_turn(self):
        self.players[self.turn].play_turn()

    def next_turn(self):
        if self.shutting_down: return
        if len(self.players) > 0:
            self.turn = (self.turn + 1) % len(self.players)
            self.play_turn()

    def notify_scrap_pile(self):
        print('scrap')
        if self.deck.peek_scrap_pile():
            self.sio.emit('scrap', room=self.name, data=self.deck.peek_scrap_pile().__dict__)
        else:
            self.sio.emit('scrap', room=self.name, data=None)

    def handle_disconnect(self, player: players.Player):
        print(f'player {player.name} left the game {self.name}')
        if player in self.players:
            if self.disconnect_bot and self.started:
                player.is_bot = True
            else:
                self.player_death(player=player, disconnected=True)
        else:
            self.dead_players.remove(player)
        if len([p for p in self.players if not p.is_bot])+len([p for p in self.dead_players if not p.is_bot]) == 0:
            print(f'no players left in game {self.name}')
            self.shutting_down = True
            self.players = []
            self.dead_players = []
            self.deck = None
            return True
        else: return False

    def player_death(self, player: players.Player, disconnected=False):
        if not player in self.players: return
        import bang.expansions.dodge_city.characters as chd
        print(player.attacker)
        if player.attacker and isinstance(player.attacker.role, roles.Sheriff) and isinstance(player.role, roles.Vice):
            for i in range(len(player.attacker.hand)):
                self.deck.scrap(player.attacker.hand.pop())
            for i in range(len(player.attacker.equipment)):
                self.deck.scrap(player.attacker.equipment.pop())
            player.attacker.notify_self()
        elif player.attacker and (isinstance(player.role, roles.Outlaw) or self.initial_players == 3):
            for i in range(3):
                player.attacker.hand.append(self.deck.draw())
            player.attacker.notify_self()
        print(f'player {player.name} died')
        if (self.waiting_for > 0):
            self.responders_did_respond_resume_turn()

        index = self.players.index(player)
        died_in_his_turn = self.started and index == self.turn
        if self.started and index <= self.turn:
            self.turn -= 1

        corpse = self.players.pop(index)
        if not disconnected:
            self.dead_players.append(corpse)
        self.notify_room()
        self.sio.emit('chat_message', room=self.name, data=f'_died|{player.name}')
        if self.started:
            self.sio.emit('chat_message', room=self.name, data=f'_died_role|{player.name}|{player.role.name}')
        for p in self.players:
            if not p.is_bot:
                p.notify_self()
        self.players_map = {c.name: i for i, c in enumerate(self.players)}
        if self.started:
            print('Check win status')
            attacker_role = None
            if player.attacker:
                attacker_role = player.attacker.role
            winners = [p for p in self.players if p.role != None and p.role.on_player_death(self.players, initial_players=self.initial_players, dead_role=player.role, attacker_role=attacker_role)]
            if len(winners) > 0:
                print('WE HAVE A WINNER')
                for p in self.players:
                    p.win_status = p in winners
                    self.sio.emit('chat_message', room=self.name, data=f'_won|{p.name}')
                    p.notify_self()
                eventlet.sleep(5.0)
                return self.reset()

            vulture = [p for p in self.players if isinstance(p.character, characters.VultureSam)]
            if len(vulture) == 0:
                for i in range(len(player.hand)):
                    self.deck.scrap(player.hand.pop())
                for i in range(len(player.equipment)):
                    self.deck.scrap(player.equipment.pop())
            else:
                for i in range(len(player.hand)):
                    vulture[0].hand.append(player.hand.pop())
                for i in range(len(player.equipment)):
                    vulture[0].hand.append(player.equipment.pop())
                vulture[0].notify_self()
            greg = [p for p in self.players if isinstance(p.character, chd.GregDigger)]
            if len(greg) > 0:
                greg[0].lives = min(greg[0].lives+2, greg[0].max_lives)
            herb = [p for p in self.players if isinstance(p.character, chd.HerbHunter)]
            if len(herb) > 0:
                herb[0].hand.append(self.deck.draw())
                herb[0].hand.append(self.deck.draw())
                herb[0].notify_self()
        
        if died_in_his_turn:
            self.next_turn()

    def reset(self):
        print('resetting lobby')
        self.players.extend(self.dead_players)
        self.dead_players = []
        self.players = [p for p in self.players if not p.is_bot]
        print(self.players)
        self.started = False
        self.waiting_for = 0
        for p in self.players:
            p.reset()
            p.notify_self()
        eventlet.sleep(0.5)
        self.notify_room()

    def get_visible_players(self, player: players.Player):
        i = self.players.index(player)
        sight = player.get_sight()
        return [{
            'name': self.players[j].name,
            'dist': min(abs(i - j), (i+ abs(j-len(self.players))), (j+ abs(i-len(self.players)))) + self.players[j].get_visibility() - (player.get_sight(countWeapon=False)-1),
            'lives': self.players[j].lives,
            'max_lives': self.players[j].max_lives,
            'is_sheriff': isinstance(self.players[j].role, roles.Sheriff),
        } for j in range(len(self.players)) if i != j]

    def notify_all(self):
        if self.started:
            data = [{
                'name': p.name,
                'ncards': len(p.hand),
                'equipment': [e.__dict__ for e in p.equipment],
                'lives': p.lives,
                'max_lives': p.max_lives,
                'is_sheriff': isinstance(p.role, roles.Sheriff),
                'is_my_turn': p.is_my_turn,
                'pending_action': p.pending_action,
                'character': p.character.__dict__ if p.character else None,
                'icon': p.role.icon if self.initial_players == 3 and p.role else '🤠'
            } for p in self.players]
            self.sio.emit('players_update', room=self.name, data=data)
