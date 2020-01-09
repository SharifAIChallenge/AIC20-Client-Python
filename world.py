import time
from abc import ABC

from model import BaseUnit, Map, King, Cell, Path, Player, GameConstants, TurnUpdates, \
    CastAreaSpell, CastUnitSpell, Unit, Spell


#################### Soalat?
# queue chie tuye world
# chera inhamme argument ezafi dare world


class World(ABC):
    DEBUGGING_MODE = False
    LOG_FILE_POINTER = None

    def __init__(self, world=None, queue=None):
        self.game_constants = None

        self.turn_updates = None

        self.map = None
        self.base_units = None
        self.current_turn = 0

        self.players = []
        self.player = None
        self.player_friend = None
        self.player_first_enemy = None
        self.player_second_enemy = None
        self.spells = None

        self.cast_spell = None

        if world is not None:
            self.game_constants = world.game_constants

            self.turn_updates = TurnUpdates(turn_updates=world.turn_updates)

            self.map = world.map
            self.base_units = world.base_units
            self.spells = world.spells
            self.current_turn = world.current_turn

            self.shortest_path = dict()
            self.players = world.players
            self.player = world.player
            self.player_friend = world.player_friend
            self.player_first_enemy = world.player_first_enemy
            self.player_second_enemy = world.player_second_enemy
            self.cast_spell = world.cast_spell
        else:
            self.queue = queue

    def get_current_time_millis(self):
        return int(round(time.time() * 1000))

    def get_time_past(self):
        return self.get_current_time_millis() - self.start_time

    def get_player_by_id(self, player_id):
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def get_spell_by_type_id(self, type_id):
        for spell in self.area_spells:
            if spell.type == type_id:
                return spell
        for spell in self.unit_spells:
            if spell.type == type_id:
                return spell
        return None

    def _game_constant_init(self, game_constants_msg):
        self.game_constants = GameConstants(max_ap=game_constants_msg["maxAP"],
                                            max_turns=game_constants_msg["maxTurns"],
                                            turn_timeout=game_constants_msg["turnTimeout"],
                                            pick_timeout=game_constants_msg["pickTimeout"],
                                            turns_to_upgrade=game_constants_msg["turnsToUpgrade"],
                                            turns_to_spell=game_constants_msg["turnsToSpell"],
                                            damage_upgrade_addition=game_constants_msg["damageUpgradeAddition"],
                                            range_upgrade_addition=game_constants_msg["rangeUpgradeAddition"])

    def _map_init(self, map_msg):
        row_num = map_msg["rows"]
        col_num = map_msg["cols"]
        paths = [Path(path["id"], [Cell(cell["row"], cell["col"]) for cell in path["cells"]]
                      ) for path in map_msg["paths"]]
        kings = [King(center=Cell(king["center"]["row"], king["center"]["col"]), hp=king["hp"],
                      attack=king["attack"], range=king["range"])
                 for king in map_msg["kings"]]
        self.players = [Player(player_id=map_msg["kings"][i]["playerId"], king=kings[i]) for i in range(4)]
        self.player = self.players[0]
        self.player_friend = self.players[1]
        self.player_first_enemy = self.players[2]
        self.player_second_enemy = self.players[3]
        self.map = Map(row_count=row_num, column_count=col_num, paths=paths, kings=kings)

    def get_unit_by_id(self, unit_id):
        for unit in self.map.units:
            if unit.unit_id == unit_id:
                return unit
        return None

    def _base_unit_init(self, msg):
        self.base_units = [BaseUnit(type_id=b_unit["typeId"], max_hp=b_unit["maxHP"],
                                                            base_attack=b_unit["baseAttack"],
                                                            base_range=b_unit["baseRange"],
                                                            target=b_unit["target"],
                                                            is_flying=b_unit["isFlying"],
                                                            is_multiple=b_unit["isMultiple"])
                                for b_unit in msg]

    def _get_base_unit_by_id(self, type_id):
        for base_unit in self.base_units:
            if base_unit.type_id == type_id:
                return base_unit
        return None

    def _spells_init(self, msg):
        self.spells = [Spell(type=spell["type"],
                             type_id=spell["typeId"],
                             duration=spell["duration"],
                             priority=spell["priority"],
                             range=spell["range"],
                             power=spell["power"],
                             target=spell["target"])
                       for spell in msg]

    def _handle_init_message(self, msg):
        # if World.DEBUGGING_MODE:
        #     if World.LOG_FILE_POINTER is not None:
        #         World.LOG_FILE_POINTER.write(str(msg))
        #         World.LOG_FILE_POINTER.write('\n')
        self._game_constant_init(msg['gameConstants'])
        self._map_init(msg["map"])
        self._base_unit_init(msg["baseUnits"])
        self._spells_init(msg["spells"])

    def _handle_turn_kings(self, msg):
        for king_msg in msg:
            hp = king_msg["hp"] if king_msg["hp"] > 0 else -1
            self.get_player_by_id(king_msg["playerId"]).king.hp = hp
            self.get_player_by_id(king_msg["playerId"]).king.target = king_msg["target"]

    def _handle_turn_units(self, msg):
        self.map.clear_units()
        for player in self.players:
            player.units.clear()
        for unit_msg in msg:
            unit_id = unit_msg["unitId"]
            player = self.get_player_by_id(player_id=unit_msg["playerId"])
            base_unit = self.base_units[unit_msg["typeId"]]
            unit = Unit(unit_id=unit_id, base_unit=base_unit,
                        cell=self.map.get_cell(unit_msg["cell"]["row"], unit_msg["cell"]["col"]),
                        path=self.map.get_path_by_id(unit_msg["pathId"]),
                        hp=unit_msg["hp"],
                        damage_level=unit_msg["damageLevel"],
                        range_level=unit_msg["rangeLevel"],
                        was_damage_upgraded=unit_msg["wasDamageUpgraded"],
                        was_range_upgraded=unit_msg["wasRangeUpgraded"],
                        is_hasted=unit_msg("isHasted"),
                        is_clone=unit_msg("isClone"),
                        active_poisons=unit_msg["activePoisons"],
                        range=unit_msg("range"),
                        attack=unit_msg("attack"),
                        was_played_this_turn=unit_msg("wasPlayedThisTurn"))
            self.map.add_unit_in_cell(unit.cell.row, unit.cell.col, unit)
            player.units.append(unit)

    def _handle_turn_cast_spells(self, msg):
        cast_spell_list = []
        for cast_spell_msg in msg:
            cast_spell = self.get_spell_by_type_id(cast_spell_msg["typeId"])
            cell = self.map.get_cell(cast_spell_msg["cell"]["row"], cast_spell_msg["cell"]["col"])
            if isinstance(cast_spell, AreaSpell):
                cast_spell_list.append(
                    CastAreaSpell(type_id=cast_spell.type, caster_id=cast_spell_msg["casterId"], center=cell,
                                  affected_units=[self.get_unit_by_id(affected_unit_id) for
                                                  affected_unit_id in
                                                  cast_spell_msg["affectedUnits"]]
                                  ))
            elif isinstance(cast_spell, UnitSpell):
                cast_spell_list.append(CastUnitSpell(type_id=cast_spell.type, caster_id=cast_spell_msg["casterId"],
                                                     target_cell=cell, unit_id=cast_spell_msg["unitId"],
                                                     path_id=cast_spell_msg["pathId"],
                                                     ))
        self.cast_spell = dict((cast_spell_i.type_id, cast_spell_i) for cast_spell_i in cast_spell_list)

    def get_cast_spell_by_type(self, type):
        return self.cast_spell[type]

    def _handle_turn_message(self, msg):
        self.current_turn = msg['currTurn']
        self.player.deck = [self._get_base_unit_by_id(deck_type_id) for deck_type_id in msg["deck"]]
        self.player.hand = [self._get_base_unit_by_id(hand_type_id) for hand_type_id in msg["hand"]]
        self._handle_turn_kings(msg["kings"])
        self._handle_turn_units(msg["units"])
        self._handle_turn_cast_spells(msg["castSpells"])

        self.turn_updates = TurnUpdates(received_spell=msg["receivedSpell"],
                                        friend_received_spell=msg["friendReceivedSpell"],
                                        got_range_upgrade=msg["gotRangeUpgrade"],
                                        got_damage_upgrade=msg["gotDamageUpgrade"],
                                        available_range_upgrades=msg["availableRangeUpgrades"],
                                        available_damage_upgrades=msg["availableDamageUpgrades"])

        self.player.spells = msg["mySpells"]
        self.player_friend.spells = msg["friendSpells"]

        self.start_time = self.get_current_time_millis()

    def pre_process_shortest_path(self):
        def path_count(path):
            shortest_path_to_cell = []
            shortest_path_to_cell_num = []
            for i in range(len(self.map.row_count)):
                l = []
                s = []
                for j in range(len(self.map.column_count)):
                    l.append(-1)
                    s.append(-1)
                shortest_path_to_cell.append(l)
                shortest_path_to_cell_num.append(s)

            count = 0
            for i in path.cells:
                if shortest_path_to_cell_num[i.row][i.col] == -1:
                    shortest_path_to_cell_num[i.row][i.col] = count
                    shortest_path_to_cell[i.row][i.col] = path
                elif shortest_path_to_cell_num[i.row][i.col] > count:
                    shortest_path_to_cell_num[i.row][i.col] = count
                    shortest_path_to_cell[i.row][i.col] = path
                count += 1
            return shortest_path_to_cell

        for p in self.players:
            paths = self.get_paths_from_player(p.player_id)
            for i in range(len(paths)):
                self.shortest_path.update({p.player_id:path_count(paths[i])})

    # in the first turn 'deck picking' give unit_ids or list of unit names to pick in that turn
    def choose_deck(self, type_ids):
        pass

    def get_my_id(self):
        pass

    def get_friend_id(self):
        pass

    def get_first_enemy_id(self):
        pass

    def get_second_enemy_id(self):
        pass

        # returns a cell that is the fortress of player with player_id

    def get_player_position(self, player_id):
        pass

        # return a list of paths starting from the fortress of player with player_id
        # the beginning is from player_id fortress cell

    def get_paths_from_player(self, player_id):
        pass

        # returns the path from player_id to its friend beginning from player_id's fortress

    def get_path_to_friend(self, player_id):
        pass

    def get_map_height(self):
        pass

    def get_map_width(self):
        pass

        # return a list of paths crossing one cell

    def get_paths_crossing_cell(self, cell):
        pass

        # return units of player that are currently in map

    def get_player_units(self, player_id):
        pass

        # return a list of units in a cell

    def get_cell_units(self, cell):
        pass

        # return the shortest path from player_id fortress to cell
        # this path is in the available path list
        # path may cross from friend

    def get_shortest_path_to_cell(self, player_id, cell):
        pass

        # returns the limit of ap for each player

    def get_max_ap(self):
        pass

        # get remaining ap

    def get_remaining_ap(self):
        pass

        # returns a list of units in hand

    def get_hand(self):
        pass

        # returns a list of units in deck

    def get_deck(self):
        pass

        # place unit with type_id in path_id

    def put_unit(self, type_id, path_id):

        pass

        # return the number of turns passed

    def get_current_turn(self):
        pass

        # return the limit of turns

    def get_max_turns(self):
        pass

        # return the time left to pick units and put in deck in the first turn

    def get_pick_timeout(self):
        pass

        # a constant limit for each turn

    def get_turn_timeout(self):
        pass

        # returns the time left for turn (miliseconds)

    def get_remaining_time(self):
        pass

        # returns the health point remaining for each player

    def get_player_hp(self, player_id):
        pass

        # put unit_id in path_id in position 'index' all spells of one kind have the same id

    def cast_unit_spell(self, unit_id, path_id, index, spell=None, spell_id=None):
        pass

        # cast spell in the cell 'center'

    def cast_area_spell(self, center, row=None, col=None, spell=None, spell_id=None):
        pass

        # returns a list of units the spell casts effects on

    def get_area_spell_targets(self, center, row=None, col=None, spell=None, spell_id=None):
        pass

        # every once in a while you can upgrade, this returns the remaining time for upgrade

    def get_remaining_turns_to_upgrade(self):
        pass

        # every once in a while a spell is given this remains the remaining time to get new spell

    def get_remaining_turns_to_get_spell(self):
        pass

        # returns area spells that are casted in last turn and returns other players spells also

    def get_cast_area_spell(self, player_id):
        pass

        # returns unit spells that are casted in last turn and returns other players spells also

    def get_cast_unit_spell(self, player_id):
        pass

    def get_active_poisons_on_unit(self, unit_id=None, unit=None):
        pass

        # returns a list of spells casted on a cell

    def get_range_upgrade_number(self, player_id):
        pass

    def get_damage_upgrade_number(self, player_id):
        pass

        # returns the token of the upgrade you can do

    def get_upgrade_token_number(self):
        pass

    def get_spells_list(self):
        pass

        # get current available spells

    def get_spells(self):
        pass

        # returns the spell given in that turn

    def get_received_spell(self):
        pass

        # returns the spell given in that turn to friend

    def get_friend_received_spell(self):
        pass

    def upgrade_unit_range(self, unit=None, unit_id=None):
        pass

    def upgrade_unit_damage(self, unit=None, unit_id=None):
        pass

    def get_player_clone_units(self, player_id):
        pass

    def get_player_hasted_units(self, player_id):
        pass

    def get_player_poisoned_units(self, player_id):
        pass

    def get_player_played_units(self, player_id):
        pass
