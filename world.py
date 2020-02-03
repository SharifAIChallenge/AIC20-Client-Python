import copy
import time
from abc import ABC

from model import BaseUnit, Map, King, Cell, Path, Player, GameConstants, TurnUpdates, \
    CastAreaSpell, CastUnitSpell, Unit, Spell, Message


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
        self.cast_spells = None

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
            self.cast_spells = world.cast_spells

            self.queue = world.queue
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
        for spell in self.spells:
            if spell.type_id == type_id:
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

        input_cells = [[Cell(row=row, col=col) for col in range(col_num)] for row in range(row_num)]

        paths = [Path(path["id"], [input_cells[cell["row"]][cell["col"]] for cell in path["cells"]]
                      ) for path in map_msg["paths"]]
        kings = [King(center=input_cells[king["center"]["row"]][king["center"]["col"]], hp=king["hp"],
                      attack=king["attack"], range=king["range"], target=None, target_cell=None, player_id=0)
                 for king in map_msg["kings"]]
        self.players = [Player(player_id=map_msg["kings"][i]["playerId"], king=kings[i]) for i in range(4)]
        self.player = self.players[0]
        self.player_friend = self.players[1]
        self.player_first_enemy = self.players[2]
        self.player_second_enemy = self.players[3]
        self.map = Map(row_num=row_num, column_num=col_num, paths=paths, kings=kings, cells=input_cells)

    def get_unit_by_id(self, unit_id):
        for unit in self.map.units:
            if unit.unit_id == unit_id:
                return unit
        return None

    def _base_unit_init(self, msg):
        self.base_units = [BaseUnit(type_id=b_unit["typeId"], max_hp=b_unit["maxHP"],
                                    base_attack=b_unit["baseAttack"],
                                    base_range=b_unit["baseRange"],
                                    target_type=b_unit["targetType"],
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

    def _handle_turn_units(self, msg, is_dead_unit=False):
        if not is_dead_unit:
            self.map.clear_units()
            for player in self.players:
                player.units.clear()
        else:
            for player in self.players:
                player.dead_units.clear()

        for unit_msg in msg:
            unit_id = unit_msg["unitId"]
            player = self.get_player_by_id(player_id=unit_msg["playerId"])
            base_unit = self.base_units[unit_msg["typeId"]]
            if not unit_msg['target'] == -1:
                tc = Cell(row=unit_msg["targetCell"]["row"], col=unit_msg["targetCell"]["col"])
            else:
                tc = None
            unit = Unit(unit_id=unit_id, base_unit=base_unit,
                        cell=self.map.get_cell(unit_msg["cell"]["row"], unit_msg["cell"]["col"]),
                        path=self.map.get_path_by_id(unit_msg["pathId"]),
                        hp=unit_msg["hp"],
                        damage_level=unit_msg["damageLevel"],
                        range_level=unit_msg["rangeLevel"],
                        is_hasted=unit_msg["isHasted"],
                        # is_clone=unit_msg.keys().isdisjoint("isClone") and unit_msg["isClone"],
                        # active_poisons=unit_msg["activePoisons"],
                        # active_poisons=unit_msg.keys().isdisjoint("activePoisons") and unit_msg["activePoisons"],
                        range=unit_msg["range"],
                        attack=unit_msg["attack"],
                        target=unit_msg["target"],
                        target_cell=tc)
            if not is_dead_unit:
                self.map.add_unit_in_cell(unit.cell.row, unit.cell.col, unit)
                player.units.append(unit)
            else:
                player.dead_units.append(unit)

    def _handle_turn_cast_spells(self, msg):
        self.cast_spells = []
        for cast_spell_msg in msg:
            cast_spell = self.get_spell_by_type_id(cast_spell_msg["typeId"])
            cell = self.map.get_cell(cast_spell_msg["cell"]["row"], cast_spell_msg["cell"]["col"])
            affected_units = [self.get_unit_by_id(affected_unit_id) for
                              affected_unit_id in
                              cast_spell_msg["affectedUnits"]]
            if cast_spell.is_area_spell():
                self.cast_spells.append(
                    CastAreaSpell(type_id=cast_spell.type_id, caster_id=cast_spell_msg["casterId"], center=cell,
                                  was_cast_this_turn=cast_spell_msg["wasCastThisTurn"],
                                  remaining_turns=cast_spell_msg["remainingTurns"],
                                  affected_units=affected_units))
            elif cast_spell.is_unit_spell():
                self.cast_spells.append(CastUnitSpell(type_id=cast_spell.type_id, caster_id=cast_spell_msg["casterId"],
                                                      target_cell=cell, unit_id=cast_spell_msg["unitId"],
                                                      path_id=cast_spell_msg["pathId"],
                                                      was_cast_this_turn=cast_spell_msg["wasCastThisTurn"],
                                                      remaining_turns=cast_spell_msg["remainingTurns"],
                                                      affected_units=affected_units))

    def get_cast_spell_by_type_id(self, type_id):
        for cast_spell in self.cast_spells:
            if cast_spell.type_id == type_id:
                return cast_spell
        return None

    def _handle_turn_message(self, msg):
        self.current_turn = msg['currTurn']
        self.player.deck = [self._get_base_unit_by_id(deck_type_id) for deck_type_id in msg["deck"]]
        self.player.hand = [self._get_base_unit_by_id(hand_type_id) for hand_type_id in msg["hand"]]
        self._handle_turn_kings(msg["kings"])
        self._handle_turn_units(msg["units"])
        # self._handle_turn_units(msg["diedUnits"], is_dead_unit=True)
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

    def _pre_process_shortest_path(self):
        def path_count(path):
            shortest_path_to_cell = []
            shortest_path_to_cell_num = []
            for i in range(self.map.row_count):
                l = []
                s = []
                for j in range(self.map.column_count):
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
                self.shortest_path.update({p.player_id: path_count(paths[i])})

    # in the first turn 'deck picking' give unit_ids or list of unit names to pick in that turn

    def choose_deck(self, type_ids=None, base_units=None):
        message = Message(type="pick", turn=self.get_current_turn(), info=None)
        if type_ids is not None:
            message.info = {"units": type_ids}
        elif base_units is not None:
            message.info = {"units": [unit.type_id for unit in base_units]}
        self.queue.put(message)

    def get_me(self):
        return self.player

    def get_friend(self):
        return self.player_friend

    def get_friend_by_id(self, player_id):
        if self.player.player_id == player_id:
            return self.player_friend
        elif self.player_friend.player_id == player_id:
            return self.player
        elif self.player_first_enemy.player_id == player_id:
            return self.player_second_enemy
        elif self.player_second_enemy.player_id == player_id:
            return self.player_first_enemy
        else:
            return None

    def get_first_enemy(self):
        return self.player_first_enemy

    def get_second_enemy(self):
        return self.player_second_enemy

    def get_map(self):
        return self.map

    # return a list of paths crossing one cell
    def get_paths_crossing_cell(self, cell=None, row=None, col=None):
        if cell is None:
            if row is None or col is None:
                return
            cell = self.map.get_cell(row, col)

        paths = []
        for p in self.map.paths:
            if cell in p.cells:
                paths.append(p)
        return paths

    # # return units of player that are currently in map
    # def get_player_units(self, player_id):
    #     player = self.get_player_by_id(player_id)
    #     return player.units

    # return a list of units in a cell
    def get_cell_units(self, cell=None, row=None, col=None):
        if cell is None:
            if row is None and col is None:
                return None
            cell = self.map.get_cell(row, col)
        return cell.units

    # return the shortest path from player_id fortress to cell
    # this path is in the available path list
    # path may cross from friend
    def get_shortest_path_to_cell(self, player_id, cell=None, row=None, col=None):
        if len(list(self.shortest_path.values())) == 0:
            self._pre_process_shortest_path()

        if cell is None:
            if row is None or col is None:
                return
            cell = self.map.get_cell(row, col)

        shortest_path_to_cell = self.shortest_path.get(player_id)
        if shortest_path_to_cell[cell.row][cell.col] == -1:
            return None

        return shortest_path_to_cell[cell.row][cell.col]

    # place unit with type_id in path_id
    def put_unit(self, type_id=None, path_id=None, base_unit=None, path=None):
        if base_unit is not None:
            type_id = base_unit.type_id
        if path is not None:
            path_id = path.path_id
        if path_id is None or type_id is None:
            return
        message = Message(turn=self.get_current_turn(),
                          type="putUnit",
                          info={
                              "typeId": type_id,
                              "pathId": path_id
                          })
        self.queue.put(message)

    # return the number of turns passed
    def get_current_turn(self):
        return self.current_turn

    # returns the time left for turn (miliseconds)
    def get_remaining_time(self):
        return self.get_turn_timeout() - self.get_time_past()

    # returns the health point remaining for each player
    # def get_player_hp(self, player_id):
    #     player = self.get_player_by_id(player_id)
    #     return player.king.hp

    # put unit_id in path_id in position 'index' all spells of one kind have the same id
    def cast_unit_spell(self, unit_id, path_id, index, spell=None, spell_id=None):
        path = None
        for p in self.map.paths:
            if p.path_id == path_id:
                path = p
                break
        cell = path.cells[index]
        if spell is None:
            spell = self.get_spell_by_type_id(spell_id)
        message = Message(type="castSpell", turn=self.get_current_turn(),
                          info={
                              "typeId": spell.type,
                              "cell": {
                                  "row": cell.row,
                                  "col": cell.col
                              },
                              "unitId": unit_id,
                              "pathId": path_id
                          })
        self.queue.put(message)

    # cast spell in the cell 'center'
    def cast_area_spell(self, center=None, row=None, col=None, spell=None, spell_id=None):
        if spell is None:
            spell = self.get_spell_by_type_id(spell_id)
        if row is not None and col is not None:
            center = self.map.get_cell(row, col)

        if center is not None:
            message = Message(type="castSpell",
                              turn=self.get_current_turn(),
                              info={
                                  "typeId": spell.type,
                                  "cell": {
                                      "row": center.row,
                                      "col": center.col
                                  },
                                  "unitId": -1,
                                  "pathId": -1
                              })
            self.queue.put(message)

    # returns a list of units the spell casts effects on
    def get_area_spell_targets(self, center, row=None, col=None, spell=None, type_id=None):
        if spell is None:
            if type_id is not None:
                spell = self.get_cast_spell_by_type_id(type_id)
        if not spell.is_area_spell:
            return []
        if center is None:
            center = Cell(row, col)
        ls = []
        for i in range(max(0, center.row - spell.range), min(center.row + spell.range, self.map.row_count)):
            for j in range(max(0, center.col - spell.range), min(center.col + spell.range, self.map.column_count)):
                cell = self.map.get_cell(i, j)
                for u in cell.units:
                    if self._is_unit_targeted(u, spell.target):
                        ls.append(u)

    def _is_unit_targeted(self, unit, spell_target):
        if spell_target == 1:
            if unit in self.player.units:
                return True
        elif spell_target == 2:
            if unit in self.player_friend or unit in self.player.units:
                return True
        elif spell_target == 3:
            if unit in self.player_first_enemy or unit in self.player_second_enemy:
                return True
        return False

    # every once in a while you can upgrade, this returns the remaining time for upgrade
    def get_remaining_turns_to_upgrade(self):
        return self.game_constants.turns_to_upgrade

    # every once in a while a spell is given this remains the remaining time to get new spell
    def get_remaining_turns_to_get_spell(self):
        return self.game_constants.turns_to_spell

    # returns a list of spells casted on a cell
    def get_range_upgrade_number(self, player_id):
        return self.turn_updates.available_range_upgrade

    def get_damage_upgrade_number(self, player_id):
        return self.turn_updates.available_damage_upgrade

    def get_spells_list(self):
        return self.player.spells

    # get current available spells as a dictionary
    def get_spells(self):
        return_dict = dict()
        for spell in self.player.spells:
            if spell in return_dict:
                return_dict[spell] += 1
            else:
                return_dict[spell] = 1
        return return_dict

    # returns the spell given in that turn
    def get_received_spell(self):
        spell_type_id = self.turn_updates.received_spell
        if spell_type_id == -1:
            return None
        else:
            return self.get_spell_by_type_id(spell_type_id)

    # returns the spell given in that turn to friend
    def get_friend_received_spell(self):
        spell_type_id = self.turn_updates.friend_received_spell
        if spell_type_id == -1:
            return None
        else:
            return self.get_spell_by_type_id(spell_type_id)

    def upgrade_unit_range(self, unit=None, unit_id=None):
        if unit is not None:
            unit_id = unit.unit_id

        elif unit_id is not None:
            self.queue.put(Message(type="rangeUpgrade",
                                   turn=self.get_current_turn(),
                                   info={
                                       "unitId": unit_id
                                   }))

    def upgrade_unit_damage(self, unit=None, unit_id=None):
        if unit is not None:
            unit_id = unit.unit_id

        elif unit_id is not None:
            self.queue.put(Message(type="damageUpgrade",
                                   turn=self.get_current_turn(),
                                   info={
                                       "unitId": unit_id
                                   }))

    def get_player_hasted_units(self, player_id):
        return [unit for unit in self.get_player_by_id(player_id=player_id).units if unit.is_hasted > 0]

    def get_player_played_units(self, player_id):
        return [unit for unit in self.get_player_by_id(player_id=player_id).units if unit.was_played_this_turn]

    def get_all_base_unit(self):
        return copy.deepcopy(self.base_units)

    def get_all_spells(self):
        return copy.deepcopy(self.spells)

    def get_spell_by_id(self, spell_id):
        for i in self.spells:
            if spell_id == i.type_id:
                return i

        return None

    def get_base_unit_by_id(self, type_id):
        for bu in self.base_units:
            if bu.type_id == type_id:
                return bu
        return None

    def get_game_constants(self):
        return self.game_constants

    def get_paths_from_player(self, player_id):
        pass
