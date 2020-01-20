from enum import Enum


class Map:
    def __init__(self, row_count, column_count, paths, kings, cells):
        self.row_count = row_count
        self.column_count = column_count
        self.paths = paths
        self.units = []
        self.kings = kings
        self.cells = cells

    def get_cell(self, row, column):
        return self.cells[row][column]

    def clear_units(self):
        for row in self.cells:
            for cell in row:
                cell.clear_units()

    def get_path_by_id(self, path_id):
        for path in self.paths:
            if path.path_id == path_id:
                return path
        return None

    def add_unit_in_cell(self, row, column, unit):
        self.cells[row][column].add_unit(unit)


class Player:
    def __init__(self, player_id, king):
        self.player_id = player_id
        self.deck = None
        self.hand = []
        self.spells = []
        self.ap = 0
        self.upgrade_tokens = 0
        self.king = king
        self.units = []

    def __str__(self):
        return "<Player | " \
               "player id : {} | " \
               "king located at ({}, {})>".format(self.player_id, self.king.center.row, self.king.center.col)


class Unit:
    def __init__(self, unit_id, base_unit, cell, path, hp, is_hasted, is_clone, damage_level,
                 range_level, was_damage_upgraded, was_range_upgraded, range, attack, active_poisons,
                 was_played_this_turn, target_id, target_cell):
        self.unit_id = unit_id
        self.base_unit = base_unit
        self.cell = cell
        self.path = path
        self.hp = hp
        self.is_hasted = is_hasted
        self.is_clone = is_clone
        self.damage_level = damage_level
        self.range_level = range_level
        self.was_damage_upgraded = was_damage_upgraded
        self.was_range_upgraded = was_range_upgraded
        self.range = range
        self.attack = attack
        self.active_poisons = active_poisons
        self.was_played_this_turn = was_played_this_turn
        self.target_id = target_id
        self.target_cell = target_cell


class SpellTarget(Enum):
    SELF = 1
    ALLIED = 2
    ENEMY = 3

    @staticmethod
    def get_value(string):
        if string == "SELF":
            return SpellTarget.SELF
        if string == "ALLIED":
            return SpellTarget.ALLIED
        if string == "ENEMY":
            return SpellTarget.ENEMY
        return None


class SpellType(Enum):
    HP = 1
    TELE = 2
    DUPLICATE = 3
    HASTE = 4

    @staticmethod
    def get_value(string):
        if string == "HP":
            return SpellType.HP
        if string == "TELE":
            return SpellType.TELE
        if string == "DUPLICATE":
            return SpellType.DUPLICATE
        if string == "HASTE":
            return SpellType.HASTE
        return None


class Spell:
    def __init__(self, type, type_id, duration, priority, range, power, target):
        self.type = SpellType.get_value(type)
        self.type_id = type_id
        self.turn_effect = duration
        self.priority = priority
        self.range = range
        self.power = power
        self.target = SpellTarget.get_value(target)

    def is_unit_spell(self):
        return self.type == SpellType.TELE

    def is_area_spell(self):
        return not self.is_unit_spell()


class Cell:
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col
        self.units = []

    def __eq__(self, other):
        if not isinstance(other, Cell):
            return NotImplemented

        return self.col == other.col and self.row == other.row

    def __str__(self):
        return "<Cell | ({}, {})>".format(self.row, self.col)

    def clear_units(self):
        self.units.clear()

    def add_unit(self, unit):
        self.units.append(unit)


class Path:
    def __init__(self, path_id=0, cells=None):
        if cells is None:
            cells = []
        self.cells = cells
        self.path_id = path_id

    def __str__(self):
        return "<Path | " \
               "path id : {} | " \
               "cells: {}>".format(self.path_id, ["({}, {})".format(cell.row, cell.col) for cell in self.cells])


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
    def __init__(self, target_id, center=None, hp=0, attack=0, range=0):
        self.center = center
        self.hp = hp
        self.attack = attack
        self.range = range
        self.target_id = target_id


class Message:
    def __init__(self, turn, type, info):
        self.type = type
        self.info = info
        self.turn = turn


class CastSpell:
    def __init__(self, type_id, caster_id, remaining_turns, was_cast_this_turn, affected_units):
        self.type_id = type_id
        self.caster_id = caster_id
        self.remaining_turns = remaining_turns
        self.was_cast_this_turn = was_cast_this_turn
        self.affected_units = affected_units


class CastUnitSpell(CastSpell):
    def __init__(self, type_id, caster_id, remaining_turns, was_cast_this_turn, affected_units
                 , target_cell, unit_id, path_id):
        super().__init__(type_id=type_id, caster_id=caster_id,
                         remaining_turns=remaining_turns,
                         was_cast_this_turn=was_cast_this_turn,
                         affected_units=affected_units)
        self.target_cell = target_cell
        self.unit_id = unit_id
        self.path_id = path_id


class CastAreaSpell(CastSpell):
    def __init__(self, type_id, caster_id, remaining_turns, was_cast_this_turn, center, affected_units):
        super().__init__(type_id=type_id, caster_id=caster_id,
                         remaining_turns=remaining_turns,
                         was_cast_this_turn=was_cast_this_turn,
                         affected_units=affected_units)
        self.center = center
        self.affected_units = affected_units


class ServerConstants:
    KEY_INFO = "info"
    KEY_TURN = "turn"
    KEY_TYPE = "type"

    CONFIG_KEY_IP = "ip"
    CONFIG_KEY_PORT = "port"
    CONFIG_KEY_TOKEN = "token"

    MESSAGE_TYPE_EVENT = "event"
    MESSAGE_TYPE_INIT = "init"
    MESSAGE_TYPE_PICK = "pick"
    MESSAGE_TYPE_SHUTDOWN = "shutdown"
    MESSAGE_TYPE_TURN = "turn"
    MESSAGE_TYPE_END_TURN = "endTurn"

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
        # if World.DEBUGGING_MODE:
        #     import datetime
        #     World.LOG_FILE_POINTER = open('client' + '-' +
        #                                   datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f") + '.log', 'w+')


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
        if turn_updates is not None:
            self.received_spell = turn_updates.received_spell
            self.friend_received_spell = turn_updates.friend_received_spell
            self.got_range_upgrade = turn_updates.got_range_upgrade
            self.got_damage_upgrade = turn_updates.got_damage_upgrade
            self.available_damage_upgrade = turn_updates.available_damage_upgrades
            self.available_range_upgrade = turn_updates.available_range_upgrades
