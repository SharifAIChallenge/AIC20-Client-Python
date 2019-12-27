from world import World


class Map:
    def __init__(self, row_count, column_count, paths, kings):
        self.row_count = row_count
        self.column_count = column_count
        self.paths = paths
        self.units = []
        self.kings = kings


class Player:
    def __init__(self, player_id, king):
        self.player_id = player_id
        self.deck = None
        self.hand = []
        self.spells = []
        self.ap = 0
        self.upgrade_tokens = 0
        self.king = king


class Unit:
    def __init__(self):
        self.unit_id = 0
        self.base_unit = None
        self.cell = None
        self.path = None
        self.hp = 0
        self.is_hasted = False


class Spell:
    def __init__(self, type_id, turn_effect):
        self.type = type_id
        self.turn_effect = turn_effect


class Cell:
    def __init__(self, row=0, col=0):
        self.row = 0
        self.col = 0
        self.units = []


class Path:
    def __init__(self, path_id=0, cells=None):
        if cells is None:
            cells = []
        self.cells = cells
        self.path_id = path_id


class Deck:
    def __init__(self):
        self.units = []


class BaseUnit:
    def __init__(self, type_id, max_hp, base_attack, base_range, target, is_flying, is_multiple):
        self.type_id = type_id
        self.max_hp = max_hp
        self.base_attack = base_attack
        self.base_range = base_range
        self.target = target
        self.is_flying = is_flying
        self.is_multiple = is_multiple


class King:
    def __init__(self, center=None, hp=0, attack=0, range=0):
        self.center = center
        self.hp = hp
        self.level = 0
        self.attack = attack
        self.range = range

class AreaSpell(Spell):
    def __init__(self, type_id, turn_effect, range, power, is_damaging):
        super().__init__(type_id=type_id, turn_effect=turn_effect)
        self.range = range
        self.power = power
        self.is_damaging = is_damaging


class UnitSpell(Spell):
    def __init__(self, type_id, turn_effect):
        super().__init__(type_id=type_id, turn_effect=turn_effect)


class Event:
    EVENT = "event‌"

    def __init__(self, type, args):
        self.type = type
        self.args = args

    def add_arg(self, arg):
        self.args.append(arg)


class ServerConstants:
    KEY_ARGS = "args"
    KEY_NAME = "name"
    KEY_TYPE = "type"

    CONFIG_KEY_IP = "ip"
    CONFIG_KEY_PORT = "port"
    CONFIG_KEY_TOKEN = "token"

    MESSAGE_TYPE_EVENT = "event"
    MESSAGE_TYPE_INIT = "init"
    MESSAGE_TYPE_PICK = "pick"
    MESSAGE_TYPE_SHUTDOWN = "shutdown"
    MESSAGE_TYPE_TURN = "turn"

    CHANGE_TYPE_ADD = "a"
    CHANGE_TYPE_DEL = "d"
    CHANGE_TYPE_MOV = "m"
    CHANGE_TYPE_ALT = "c"


class GameConstants:
    def __init__(self, max_ap, max_turns, turn_timeout, pick_timeout,
                 turns_to_upgrade, turns_to_spell, damage_upgrade_addition, range_upgrade_addition):
        self.max_ap = max_ap
        self.max_turns = max_turns
        self.turn_timeout = turn_timeout
        self.pick_timeout = pick_timeout
        self.turns_to_upgrade = turns_to_upgrade
        self.turns_to_spell = turns_to_spell
        self.damage_upgrade_addition = damage_upgrade_addition
        self.range_upgrade_addition = range_upgrade_addition
        if World.DEBUGGING_MODE:
            import datetime
            World.LOG_FILE_POINTER = open('client' + '-' +
                                          datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f") + '.log', 'w+')

class TurnUpdates:
    def __init__(self, received_spell=None, friend_received_spell=None,
                got_range_upgrade=None, got_damage_upgrade=None,
	            available_range_upgrades=None, available_damage_upgrades=None, turn_updates=None):
        self.received_spell = received_spell
        self.friend_received_spell = friend_received_spell
        self.got_range_upgrade = got_range_upgrade
        self.got_damage_upgrade = got_damage_upgrade
        self.available_damage_upgrade = available_damage_upgrades
        self.available_range_upgrade = available_range_upgrades
        if turn_updates != None:
            self.received_spell = turn_updates.received_spell
            self.friend_received_spell = turn_updates.friend_received_spell
            self.got_range_upgrade = turn_updates.got_range_upgrade
            self.got_damage_upgrade = turn_updates.got_damage_upgrade
            self.available_damage_upgrade = turn_updates.available_damage_upgrades
            self.available_range_upgrade = turn_updates.available_range_upgrades
