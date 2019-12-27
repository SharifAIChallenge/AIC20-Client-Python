from abc import ABC
import time

from model import AreaSpell, UnitSpell, BaseUnit, Map, King, Cell, Path, Player, GameConstants, TurnUpdates


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
        self.area_spells = None
        self.unit_spells = None
        self.current_turn = 0

        self.players = []
        self.player = None
        self.player_friend = None
        self.player_first_enemy = None
        self.player_second_enemy = None

        if world is not None:
            self.game_constants = world.game_constants

            self.turn_updates = TurnUpdates(turn_updates=world.turn_updates)

            self.map = world.map
            self.base_units = world.base_units
            self.area_spells = world.area_spells
            self.unit_spells = world.unit_spells
            self.current_turn = world.current_turn
            self.received_spell = world.received_spell
            self.friend_received_spell = world.friend_received_spell

            self.players = world.players
            self.player = world.player
            self.player_friend = world.player_friend
            self.player_first_enemy = world.player_first_enemy
            self.player_second_enemy = world.player_second_enemy
            # game_constants = world._get_game_constants()
            # self.game_constants = game_constants
            # self.max_ap = game_constants.max_ap
            # self.max_turns = game_constants.max_turns
            # self.kill_score = game_constants.kill_score
            # self.objective_zone_score = game_constants.objective_zone_score
            # self.max_score = game_constants.max_score
            # self.total_move_phases = game_constants.total_move_phases
            # self.init_overtime = game_constants.init_overtime
            # self.hero_constants = world.hero_constants
            # self.ability_constants = world.ability_constants
            # self.map = world.map
            # self.queue = world.queue
            # self.heroes = world.heroes
            # self.max_score_diff = world.max_score_diff
        else:
            self.queue = queue  ######################in chieeeeee?!!!!!!!!!!!!!!!!!#############

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
        paths = [Path(path["id"], [Cell(cell["row"], cell["column"]) for cell in path["cells"]]
                      ) for path in map_msg["paths"]]
        kings = [King(center=Cell(king["row"], king["col"]), hp=king["hp"],
                      attack=king["attack"], range=king["range"])
                 for king in map_msg["kings"]]
        self.players = [Player(player_id=map_msg["kings"][i]["playerId"], king=kings[i]) for i in range(4)]
        self.players_by_id = dict([(player.player_id, player) for player in self.players])
        self.player = self.players[0]
        self.player_friend = self.players[1]
        self.player_first_enemy = self.players[2]
        self.player_second_enemy = self.players[3]
        self.map = Map(row_count=row_num, column_count=col_num, paths=paths, kings=kings)

    def _base_unit_init(self, msg):
        self.base_units = dict([(b_unit["typeId"], BaseUnit(type_id=b_unit["typeId"], max_hp=b_unit["maxHP"], base_attack=b_unit["baseAttack"],
                                    base_range=b_unit["baseRange"], target=b_unit["target"],
                                    is_flying=b_unit["isFlying"],
                                    is_multiple=b_unit["isMultiple"]))
                           for b_unit in msg])

    def _spells_init(self, msg):
        for spell in msg:
            if msg["isAreaSpell"]:
                self.area_spells.append(AreaSpell(type_id=spell["typeId"], turn_effect=spell["turnEffect"],
                                                  range=spell["range"], power=spell["power"],
                                                  is_damaging=spell["isDamaging"]))
            else:
                self.unit_spells.append(UnitSpell(type_id=spell["typeId"], turn_effect=spell["turnEffect"]))

    def _handle_init_message(self, msg):
        # if World.DEBUGGING_MODE:
        #     if World.LOG_FILE_POINTER is not None:
        #         World.LOG_FILE_POINTER.write(str(msg))
        #         World.LOG_FILE_POINTER.write('\n')
        msg = msg['args'][0]
        self._game_constant_init(msg['gameConstants'])
        self._map_init(msg["map"])
        self._base_unit_init(msg["baseUnits"])
        self._spells_init(msg["spells"])

    def _handle_turn_kings(self, msg):
        for king_msg in msg:
            hp = king_msg["hp"] if king_msg["hp"] >= 0 else -1
            self.players_by_id[king_msg["playerId"]].king.hp = hp

    def _handle_turn_units(self, msg):
        pass

    def _handle_turn_cast_spells(self, msg):
        pass

    def _handle_turn_message(self, msg):
        self.current_turn = msg['currTurn']
        self.player.deck = [self.base_units[deck["typeId"]] for deck in msg["deck"]]
        self.player.hand = [self.base_units[hand["typeId"]] for hand in msg["hand"]]
        self._handle_turn_kings(msg["kings"])
        self._handle_turn_units(msg["units"])
        self._handle_turn_cast_spells(msg["castSpells"])

        self.turn_updates = TurnUpdates(received_spell=msg["receivedSpell"], friend_received_spell=msg["friendReceivedSpell"],
                                        got_range_upgrade=msg["gotRangeUpgrade"], got_damage_upgrade=msg["gotDamageUpgrade"],
                                        available_range_upgrades=msg["availableRangeUpgrades"],
                                        available_damage_upgrades=msg["availableDamageUpgrades"])

        self.player.spells = msg["mySpells"]
        self.player_friend.spells = msg["friendSpells"]

        self.start_time = self.get_current_time_millis()

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
