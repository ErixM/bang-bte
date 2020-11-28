from typing import List
from bang.characters import *

class PixiePete(Character):
    def __init__(self):
        super().__init__("Pixie Pete", max_lives=3)
        self.desc = "Pesca 3 carte invece che 2"
        self.icon = '☘️'

class TequilaJoe(Character):
    def __init__(self):
        super().__init__("Tequila Joe", max_lives=4)
        self.desc = "Le birre gli fanno recuperare 2 vite"
        self.icon = '🍻'

class GregDigger(Character):
    def __init__(self):
        super().__init__("Greg Digger", max_lives=4)
        self.desc = "Quando un giocatore muore, recupera 2 vite"
        self.icon = '🦴'

class HerbHunter(Character):
    def __init__(self):
        super().__init__("HerbHunter", max_lives=4)
        self.desc = "Quando un giocatore muore, ottiene 2 carte"
        self.icon = '⚰️'

class ElenaFuente(Character):
    def __init__(self):
        super().__init__("Elena Fuente", max_lives=3)
        self.desc = "Può usare una carta qualsiasi come mancato"
        self.icon = '🧘‍♀️'

class BillNoface(Character):
    def __init__(self):
        super().__init__("Bill Noface", max_lives=4)
        self.desc = "Pesca 1 carta + 1 carta per ogni ferita"
        self.icon = '🙈'

def all_characters() -> List[Character]:
    return [
        PixiePete(),
        TequilaJoe(),
        GregDigger(),
        HerbHunter(),
        ElenaFuente(),
        BillNoface(),
    ]