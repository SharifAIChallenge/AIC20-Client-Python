from enum import Enum


class Map:
    def __init__(self, row_num, col_num, paths, units, kings, cells):
        self.row_num = row_num
        self.col_num = col_num
        self.paths = paths
        self.paths_dict = dict([(path.id, path) for path in paths])
        self.units = units
        self.kings = kings
        self.cells = cells

    def get_cell(self, row, col):
        return self.cells[row][col]

    def clear_units(self):
        for row in self.cells:
            for cell in row:
                cell.clear_units()

    def get_path_by_id(self, path_id):
        return None if not path_id in self.paths_dict else self.paths_dict[path_id]

    def add_unit_in_cell(self, row, col, unit):
        self.cells[row][col].add_unit(unit)


class Player:
    def __init__(self, player_id, deck, hand, ap, king, paths_from_player, path_to_friend,
                 units, cast_area_spell, cast_unit_spell, duplicate_units, hasted_units, played_units,
                 died_units, spells, range_upgraded_unit=None, damage_upgraded_unit=None):
        self._spells_dict = {}
        self.player_id = player_id
        self.deck = deck
        self.hand = hand
        self.ap = ap
        self.king = king
        self.paths_from_player = paths_from_player
        self.path_to_friend = path_to_friend
        self.units = units  # alive units
        self.cast_area_spell = cast_area_spell
        self.cast_unit_spell = cast_unit_spell
        self.duplicate_units = duplicate_units
        self.hasted_units = hasted_units
        self.played_units = played_units  # units that played last turn
        self.died_units = died_units  # units that died last turn
        self.spells = spells
        self.range_upgraded_unit = range_upgraded_unit  # unit that last turn the player upgraded range of it
        self.damage_upgraded_unit = damage_upgraded_unit  # unit that last turn the player upgraded damage of it

    def is_alive(self):
        return self.king.is_alive

    def get_hp(self):
        return self.king.hp

    def set_spells(self, spells):
        self.spells = spells
        for spell in spells:
            if spell.type_id in self._spells_dict:
                self._spells_dict[spell.type_id] += 1
            else:
                self._spells_dict[spell.type_id] = 1

    def get_spell_count(self, spell=None, spell_id=None):
        if spell is not None:
            spell_id = spell.type_id
        if spell_id in self._spells_dict:
            return self._spells_dict[spell_id]
        return 0

    def get_spells(self):
        return self.spells

    def __str__(self):
        return "<Player | " \
               "player id : {} | " \
               "king located at ({}, {})>".format(self.player_id, self.king.center.row, self.king.center.col)


class Unit:
    def __init__(self, base_unit, cell, unit_id, hp, path, target, target_cell,
                 target_if_king, player_id, damage_level, range_level, range,
                 attack, is_duplicate, is_hasted, affected_spells):
        self.base_unit = base_unit
        self.cell = cell
        self.unit_id = unit_id
        self.hp = hp
        self.path = path
        self.target = target
        self.target_cell = target_cell
        self.target_if_king = target_if_king
        self.player_id = player_id
        self.damage_level = damage_level
        self.range_level = range_level
        self.range = range
        self.attack = attack
        self.is_duplicate = is_duplicate
        self.is_hasted = is_hasted
        self.affected_spells = affected_spells


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


class UnitTarget(Enum):
    GROUND = 1
    AIR = 2
    BOTH = 3

    @staticmethod
    def get_value(string):
        if string == "GROUND":
            return UnitTarget.GROUND
        if string == "AIR":
            return UnitTarget.AIR
        if string == "BOTH":
            return UnitTarget.BOTH
        return None


class Spell:
    def __init__(self, type, type_id, duration, priority, target, range, power, is_damaging):
        self.type = type
        self.type_id = type_id
        self.duration = duration
        self.priority = priority
        self.target = target
        self.range = range
        self.power = power
        self.is_damaging = is_damaging

    def is_unit_spell(self):
        return self.type == SpellType.TELE

    def is_area_spell(self):
        return not self.is_unit_spell()

    def __eq__(self, other):
        return self.type_id == other.type_id

    def __str__(self):
        return "<Spell | " \
               "type : {} | " \
               "type id : {}>".format(self.type, self.type_id)


class Cell:
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col
        self.units = []  # private access

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
    def __init__(self, id=None, cells=None, path=None):
        if id is not None and cells is not None:
            self.cells = cells
            self.id = id
        if path is not None:
            self.id = path.id
            self.cells = []
            for cell in path.cells:
                self.cells.append(cell)

    def __str__(self):
        return "<Path | " \
               "path id : {} | " \
               "cells: {}>".format(self.id, ["({}, {})".format(cell.row, cell.col) for cell in self.cells])

    def __eq__(self, other):
        return self.id == other.id


class Deck:
    def __init__(self):
        self.units = []


class BaseUnit:
    def __init__(self, type_id, max_hp, base_attack, base_range, target_type, is_flying, is_multiple, ap):
        self.type_id = type_id
        self.max_hp = max_hp
        self.base_attack = base_attack
        self.base_range = base_range
        self.target_type = target_type
        self.is_flying = is_flying
        self.is_multiple = is_multiple
        self.ap = ap

    def __str__(self):
        return "<BaseUnit | " \
               "type id : {}>".format(self.type_id)


class King:
    def __init__(self, center, hp, attack, range, is_alive, player_id,
                 target, target_cell):
        self.center = center
        self.hp = hp
        self.attack = attack
        self.range = range
        self.is_alive = is_alive
        self.player_id = player_id
        self.target = target
        self.target_cell = target_cell


class Message:
    def __init__(self, turn, type, info):
        self.type = type
        self.info = info
        self.turn = turn


class CastSpell:
    def __init__(self, spell, id, caster_id, cell, affected_units):
        self.spell = spell
        self.id = id
        self.caster_id = caster_id
        self.cell = cell
        self.affected_units = affected_units


class CastUnitSpell(CastSpell):
    def __init__(self, spell, id, caster_id, cell, affected_units
                 , unit, path):
        super().__init__(spell=spell, id=id, caster_id=caster_id,
                         cell=cell, affected_units=affected_units)
        self.unit = unit
        self.path = path


class CastAreaSpell(CastSpell):
    def __init__(self, spell, id, caster_id, cell, affected_units,
                 remaining_turns):
        super().__init__(spell=spell, id=id, caster_id=caster_id,
                         cell=cell, affected_units=affected_units)
        self.ramaining_turns = remaining_turns


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
                 turns_to_upgrade, turns_to_spell, damage_upgrade_addition, range_upgrade_addition,
                 deck_size, hand_size):
        self.max_ap = max_ap
        self.max_turns = max_turns
        self.turn_timeout = turn_timeout
        self.pick_timeout = pick_timeout
        self.turns_to_upgrade = turns_to_upgrade
        self.turns_to_spell = turns_to_spell
        self.damage_upgrade_addition = damage_upgrade_addition
        self.range_upgrade_addition = range_upgrade_addition
        self.deck_size = deck_size
        self.hand_size = hand_size


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
