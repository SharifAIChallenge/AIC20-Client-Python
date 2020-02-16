import copy
import time
from abc import ABC

from model import BaseUnit, Map, King, Cell, Path, Player, GameConstants, TurnUpdates, \
    CastAreaSpell, CastUnitSpell, Unit, Spell, Message, UnitTarget, SpellType, SpellTarget


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
        self.spells = []
        self.cast_spells = []

        if world is not None:
            self.game_constants = world.game_constants

            self.turn_updates = TurnUpdates(turn_updates=world.turn_updates)

            self.map = world.map
            self.base_units = world.base_units
            self.spells = world.spells
            self.current_turn = world.current_turn

            self.players = world.players
            self.player = world.player
            self.player_friend = world.player_friend
            self.player_first_enemy = world.player_first_enemy
            self.player_second_enemy = world.player_second_enemy
            self.cast_spells = world.cast_spells

            self.queue = world.queue
        else:
            self.queue = queue

    def _get_current_time_millis(self):
        return int(round(time.time() * 1000))

    def _get_time_past(self):
        return self._get_current_time_millis() - self.start_time

    def _game_constant_init(self, game_constants_msg):
        self.game_constants = GameConstants(max_ap=game_constants_msg["maxAP"],
                                            max_turns=game_constants_msg["maxTurns"],
                                            turn_timeout=game_constants_msg["turnTimeout"],
                                            pick_timeout=game_constants_msg["pickTimeout"],
                                            turns_to_upgrade=game_constants_msg["turnsToUpgrade"],
                                            turns_to_spell=game_constants_msg["turnsToSpell"],
                                            damage_upgrade_addition=game_constants_msg["damageUpgradeAddition"],
                                            range_upgrade_addition=game_constants_msg["rangeUpgradeAddition"],
                                            hand_size=game_constants_msg["handSize"],
                                            deck_size=game_constants_msg["deckSize"])

    def _find_path_starting_and_ending_with(self, first, last, paths):
        for path in paths:
            c_path = Path(path=path)
            if c_path.cells[0] == first and c_path.cells[-1] == last:
                return c_path
            c_path.cells.reverse()
            if c_path.cells[0] == first and c_path.cells[-1] == last:
                return c_path
        return None

    def _map_init(self, map_msg):
        row_num = map_msg["rows"]
        col_num = map_msg["cols"]

        input_cells = [[Cell(row=row, col=col) for col in range(col_num)] for row in range(row_num)]

        paths = [Path(id=path["id"], cells=[input_cells[cell["row"]][cell["col"]] for cell in path["cells"]]
                      ) for path in map_msg["paths"]]
        kings = [King(player_id=king["playerId"], center=input_cells[king["center"]["row"]][king["center"]["col"]],
                      hp=king["hp"],
                      attack=king["attack"], range=king["range"], target=None, target_cell=None, is_alive=True)
                 for king in map_msg["kings"]]

        self.players = [Player(player_id=map_msg["kings"][i]["playerId"], king=kings[i], deck=[],
                               hand=[], ap=self.game_constants.max_ap,
                               paths_from_player=self._get_paths_starting_with(kings[i].center, paths),
                               path_to_friend=self._find_path_starting_and_ending_with(kings[i].center,
                                                                                       kings[i ^ 1].center, paths),
                               units=[], cast_area_spell=None, cast_unit_spell=None,
                               duplicate_units=[],
                               hasted_units=[],
                               played_units=[],
                               died_units=[],
                               range_upgraded_unit=None,
                               damage_upgraded_unit=None,
                               spells=[]) for i in range(4)]

        for player in self.players:
            player.paths_from_player.remove(player.path_to_friend)

        self.player = self.players[0]
        self.player_friend = self.players[1]
        self.player_first_enemy = self.players[2]
        self.player_second_enemy = self.players[3]

        self.map = Map(row_num=row_num, col_num=col_num, paths=paths, kings=kings, cells=input_cells, units=[])

    def _base_unit_init(self, msg):
        self.base_units = [BaseUnit(type_id=b_unit["typeId"], max_hp=b_unit["maxHP"],
                                    base_attack=b_unit["baseAttack"],
                                    base_range=b_unit["baseRange"],
                                    target_type=UnitTarget.get_value(b_unit["target"]),
                                    is_flying=b_unit["isFlying"],
                                    is_multiple=b_unit["isMultiple"],
                                    ap=b_unit["ap"])
                           for b_unit in msg]

    def _get_base_unit_by_id(self, type_id):
        for base_unit in self.base_units:
            if base_unit.type_id == type_id:
                return base_unit
        return None

    def _spells_init(self, msg):
        self.spells = [Spell(type=SpellType.get_value(spell["type"]),
                             type_id=spell["typeId"],
                             duration=spell["duration"],
                             priority=spell["priority"],
                             range=spell["range"],
                             power=spell["power"],
                             target=SpellTarget.get_value(spell["target"]),
                             is_damaging=False)
                       for spell in msg]

    def _handle_init_message(self, msg):
        self._game_constant_init(msg['gameConstants'])
        self._map_init(msg["map"])
        self._base_unit_init(msg["baseUnits"])
        self._spells_init(msg["spells"])

    def _handle_turn_kings(self, msg):
        for king_msg in msg:
            hp = king_msg["hp"] if (king_msg["hp"] > 0 and king_msg["isAlive"]) else -1
            self.get_player_by_id(king_msg["playerId"]).king.hp = hp
            self.get_player_by_id(king_msg["playerId"]).king.target = king_msg["target"] if king_msg[
                                                                                                "target"] != -1 else None

    def _handle_turn_units(self, msg, is_dead_unit=False):
        if not is_dead_unit:
            self.map.clear_units()
            for player in self.players:
                player.units.clear()
                player.played_units.clear()
                player.hasted_units.clear()
                player.duplicate_units.clear()
                player.range_upgraded_unit = None
                player.damage_upgraded_unit = None
        else:
            for player in self.players:
                player.died_units.clear()

        for unit_msg in msg:
            unit_id = unit_msg["unitId"]
            player = self.get_player_by_id(player_id=unit_msg["playerId"])
            base_unit = self.base_units[unit_msg["typeId"]]

            if not unit_msg['target'] == -1:
                target_cell = Cell(row=unit_msg["targetCell"]["row"], col=unit_msg["targetCell"]["col"])
            else:
                target_cell = None
            unit = Unit(unit_id=unit_id, base_unit=base_unit,
                        cell=self.map.get_cell(unit_msg["cell"]["row"], unit_msg["cell"]["col"]),
                        path=self.map.get_path_by_id(unit_msg["pathId"]),
                        hp=unit_msg["hp"],
                        damage_level=unit_msg["damageLevel"],
                        range_level=unit_msg["rangeLevel"],
                        is_duplicate=unit_msg["isDuplicate"],
                        is_hasted=unit_msg["isHasted"],
                        range=unit_msg["range"],
                        attack=unit_msg["attack"],
                        target=unit_msg["target"],
                        target_cell=target_cell,
                        affected_spells=[self.get_cast_spell_by_id(cast_spell_id) for cast_spell_id in
                                         unit_msg["affectedSpells"]],
                        target_if_king=None if self.get_player_by_id(
                            unit_msg["target"]) is None else self.get_player_by_id(unit_msg["target"]).king,
                        player_id=unit_msg["playerId"])
            if not is_dead_unit:
                self.map.add_unit_in_cell(unit.cell.row, unit.cell.col, unit)
                player.units.append(unit)
                if unit_msg["wasDamageUpgraded"]:
                    player.damage_upgraded_unit = unit
                if unit_msg["wasRangeUpgraded"]:
                    player.range_upgraded_unit = unit
                if unit_msg["wasPlayedThisTurn"]:
                    player.played_units.append(unit)
                if unit.is_hasted:
                    player.hasted_units.append(unit)
                if unit.is_duplicate:
                    player.duplicate_units.append(unit)
            else:
                player.died_units.append(unit)
        for unit in self.map.units:
            if unit.target == -1 or unit.target_if_king is not None:
                unit.target = None
            else:
                unit.target = self.map.get_unit_by_id(unit.target)

    def _handle_turn_cast_spells(self, msg):
        self.cast_spells = []
        for cast_spell_msg in msg:
            spell = self.get_spell_by_id(cast_spell_msg["typeId"])
            cell = self.map.get_cell(cast_spell_msg["cell"]["row"], cast_spell_msg["cell"]["col"])
            affected_units = [self.get_unit_by_id(affected_unit_id) for
                              affected_unit_id in
                              cast_spell_msg["affectedUnits"]]
            if spell.is_area_spell():
                self.cast_spells.append(
                    CastAreaSpell(spell=spell, id=cast_spell_msg["id"],
                                  caster_id=cast_spell_msg["casterId"], cell=cell,
                                  remaining_turns=cast_spell_msg["remainingTurns"],
                                  affected_units=affected_units))
            elif spell.is_unit_spell():
                self.cast_spells.append(
                    CastUnitSpell(spell=spell, id=cast_spell_msg["id"],
                                  caster_id=cast_spell_msg["casterId"],
                                  cell=cell,
                                  unit=self.get_unit_by_id(cast_spell_msg["unitId"]),
                                  path=self.map.get_path_by_id(cast_spell_msg["pathId"]),
                                  affected_units=affected_units))

    def get_cast_spell_by_id(self, id):
        for cast_spell in self.cast_spells:
            if cast_spell.id == id:
                return cast_spell
        return None

    def _handle_turn_message(self, msg):
        self.current_turn = msg['currTurn']
        self.player.deck = [self._get_base_unit_by_id(deck_type_id) for deck_type_id in msg["deck"]]
        self.player.hand = [self._get_base_unit_by_id(hand_type_id) for hand_type_id in msg["hand"]]
        self._handle_turn_kings(msg["kings"])
        self._handle_turn_units(msg["units"])
        self._handle_turn_units(msg=msg["diedUnits"], is_dead_unit=True)
        self._handle_turn_cast_spells(msg["castSpells"])

        self.turn_updates = TurnUpdates(received_spell=msg["receivedSpell"],
                                        friend_received_spell=msg["friendReceivedSpell"],
                                        got_range_upgrade=msg["gotRangeUpgrade"],
                                        got_damage_upgrade=msg["gotDamageUpgrade"],
                                        available_range_upgrades=msg["availableRangeUpgrades"],
                                        available_damage_upgrades=msg["availableDamageUpgrades"])

        self.player.set_spells([self.get_spell_by_id(spell_id) for spell_id in msg["mySpells"]])
        self.player_friend.set_spells([self.get_spell_by_id(spell_id) for spell_id in msg["friendSpells"]])
        self.player.ap = msg["remainingAP"]

        self.start_time = self._get_current_time_millis()

    def choose_deck_by_id(self, type_ids):
        message = Message(type="pick", turn=self.get_current_turn(), info=None)
        if type_ids is not None:
            message.info = {"units": type_ids}
            self.queue.put(message)

    # in the first turn 'deck picking' give unit_ids or list of unit names to pick in that turn
    def choose_deck(self, base_units):
        message = Message(type="pick", turn=self.get_current_turn(), info=None)
        if base_units is not None:
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
    def get_shortest_path_to_cell(self, from_player_id=None, from_player=None, cell=None, row=None, col=None):
        def path_count(paths):
            shortest_path = None
            count = 0
            for p in paths:
                count_num = 0
                for c in p.cells:
                    if c == cell:
                        if shortest_path is None:
                            count = count_num
                            shortest_path = p

                        elif count_num < count:
                            count = count_num
                            shortest_path = p
                    count_num += 1
            return shortest_path

        if from_player is not None:
            from_player_id = from_player.player_id
        if cell is None:
            if row is None or col is None:
                return
            cell = self.map.get_cell(row, col)
        p = path_count(self.get_player_by_id(from_player_id).paths_from_player)
        if p is None:
            ls = [self.get_player_by_id(from_player_id).path_to_friend]
            ptf = path_count(ls)
            if ptf is None:
                pff = path_count(self.get_friend_by_id(from_player_id).paths_from_player)
                if pff is None:
                    return None
                return pff
            return ptf
        return p

    # place unit with type_id in path_id
    def put_unit(self, type_id=None, path_id=None, base_unit=None, path=None):
        if base_unit is not None:
            type_id = base_unit.type_id
        if path is not None:
            path_id = path.id
        if path_id is None or type_id is None:
            return None
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

    def get_remaining_time(self):
        return self.game_constants.turn_timeout - self._get_time_past()

    # put unit_id in path_id in position 'index' all spells of one kind have the same id
    def cast_unit_spell(self, unit=None, unit_id=None, path=None, path_id=None, cell=None, row=None, col=None,
                        spell=None,
                        spell_id=None):
        if spell is None and spell_id is None:
            return None
        if spell is None:
            spell = self.get_spell_by_id(spell_id)
        if row is not None and col is not None:
            cell = Cell(row, col)
        if unit is not None:
            unit_id = unit.unit_id
        if path is not None:
            path_id = path.id
        message = Message(type="castSpell", turn=self.get_current_turn(),
                          info={
                              "typeId": spell.type_id,
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
            spell = self.get_spell_by_id(spell_id)
        if row is not None and col is not None:
            center = self.map.get_cell(row, col)

        if center is not None:
            message = Message(type="castSpell",
                              turn=self.get_current_turn(),
                              info={
                                  "typeId": spell.type_id,
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
                spell = self.get_cast_spell_by_id(type_id)
            else:
                return []
        if not spell.is_area_spell():
            return []
        if center is None:
            center = Cell(row, col)
        ls = []
        for i in range(max(0, center.row - spell.range), min(center.row + spell.range, self.map.row_num)):
            for j in range(max(0, center.col - spell.range), min(center.col + spell.range, self.map.col_num)):
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
        rem_turn = (self.game_constants.turns_to_upgrade - self.current_turn) % self.game_constants.turns_to_upgrade
        if rem_turn == 0:
            return self.game_constants.turns_to_upgrade
        return rem_turn

    # every once in a while a spell is given this remains the remaining time to get new spell
    def get_remaining_turns_to_get_spell(self):
        rem_turn = (self.game_constants.turns_to_spell - self.current_turn) % self.game_constants.turns_to_spell
        if rem_turn == 0:
            return self.game_constants.turns_to_spell
        return rem_turn

    # returns a list of spells casted on a cell
    def get_range_upgrade_number(self):
        return self.turn_updates.available_range_upgrade

    def get_damage_upgrade_number(self):
        return self.turn_updates.available_damage_upgrade

    # returns the spell given in that turn
    def get_received_spell(self):
        spell_id = self.turn_updates.received_spell
        spell = self.get_spell_by_id(spell_id)
        return spell

    # returns the spell given in that turn to friend
    def get_friend_received_spell(self):
        spell_id = self.turn_updates.friend_received_spell
        spell = self.get_spell_by_id(spell_id)
        return spell

    def upgrade_unit_range(self, unit=None, unit_id=None):
        if unit is not None:
            unit_id = unit.unit_id

        if unit_id is not None:
            self.queue.put(Message(type="rangeUpgrade",
                                   turn=self.get_current_turn(),
                                   info={
                                       "unitId": unit_id
                                   }))

    def upgrade_unit_damage(self, unit=None, unit_id=None):
        if unit is not None:
            unit_id = unit.unit_id

        if unit_id is not None:
            self.queue.put(Message(type="damageUpgrade",
                                   turn=self.get_current_turn(),
                                   info={
                                       "unitId": unit_id
                                   }))

    def get_all_base_unit(self):
        return copy.deepcopy(self.base_units)

    def get_all_spells(self):
        return copy.deepcopy(self.spells)

    def get_king_by_id(self, player_id):
        for p in self.players:
            if p.player_id == player_id:
                return p.king

        return None

    def get_base_unit_by_id(self, type_id):
        for bu in self.base_units:
            if bu.type_id == type_id:
                return bu
        return None

    # returns unit in map with a unit_id
    def get_unit_by_id(self, unit_id):
        for unit in self.map.units:
            if unit.unit_id == unit_id:
                return unit
        return None

    def get_player_by_id(self, player_id):
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def get_spell_by_id(self, type_id):
        for spell in self.spells:
            if spell.type_id == type_id:
                return spell
        return None

    def get_game_constants(self):
        return self.game_constants

    def _get_paths_starting_with(self, first, paths):
        ret = []
        for path in paths:
            c_path = Path(path=path)
            if c_path.cells[-1] == first:
                c_path.cells.reverse()
            if c_path.cells[0] == first:
                ret.append(c_path)
        return ret

    def _handle_end_message(self, scores_list_msg):
        return dict([(score["playerId"], score["score"]) for score in scores_list_msg])
