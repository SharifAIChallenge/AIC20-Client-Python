class Map:
    def __init__(self):
        self.width = 0
        self.heigth = 0
        self.path = []
        self.units = []
        self.kings = []


class Player:
    def __init__(self):
        self.playerId = 0
        self.deck = None
        self.hand = None
        self.spells = []
        self.ap = 0
        self.hp = 0
        self.isAlive = True
        self.upgradeTokens = 0
        self.king = 0


class Unit:
    def __init__(self):
        self.unitId = 0
        self.baseUnit = None
        self.cell = None
        self.path = None
        self.hp = 0
        self.isHasted = False


class Spell:
    def __init__(self):
        self.type = None
        self.turnEffect = None


class Cell:
    def __init__(self):
        self.row = 0
        self.col = 0
        self.units = []


class Path:
    def __init__(self):
        self.cells = []
        self.pathId = 0


class Hand:
    def __init__(self):
        self.units = []


class Deck:
    def __init__(self):
        self.units = []


class BaseUnit:
    def __init__(self):
        self.type = None
        self.maxHP = 0
        self.attack = None
        self.level = None
        self.range = None
        self.target = None
        self.isFlying = False
        self.isMultiple = False


class King:
    def __init__(self):
        self.playerId = 0
        self.center = None
        self.hp = 0
        self.level = None
        self.attack = None
        self.range = None


class AreaSpell(Spell):
    def __init__(self):
        super().__init__()
        self.range = None
        self.power = None
        self.isDamaging = False


class UnitSpell(Spell):
    def __init__(self):
        super().__init__()
