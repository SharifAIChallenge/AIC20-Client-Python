from model import Event, CastUnitSpell, CastAreaSpell
from world import World


class Game(World):
    # in the first turn 'deck picking' give unit_ids or list of unit names to pick in that turn

    def choose_deck(self, type_ids):
        for t in type_ids:
            base_unit = self.base_units.get(t, None)
            if base_unit is not None:
                self.player.deck.units.append(base_unit)

    def get_my_id(self):
        return self.player.player_id

    def get_friend_id(self):
        return self.player_friend.player_id

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

    def get_first_enemy_id(self):
        return self.player_first_enemy.player_id

    def get_second_enemy_id(self):
        return self.player_second_enemy.player_id

    # returns a cell that is the fortress of player with player_id
    def get_player_position(self, player_id):
        player = self.get_player_by_id(player_id)
        if player is not None:
            return player.king.center

    # return a list of paths starting from the fortress of player with player_id
    # the beginning is from player_id fortress cell
    def get_paths_from_player(self, player_id):
        paths = []
        player_king_cell = self.get_player_position(player_id)
        for p in self.map.paths:
            first_cell = p.cells[0]
            last_cell = p.cells[len(p.cells) - 1]
            if first_cell == player_king_cell:
                paths.append(p)
                continue
            if last_cell == player_king_cell:
                p.cells.reverse()
                paths.append(p)
                continue

    # returns the path from player_id to its friend beginning from player_id's fortress
    def get_path_to_friend(self, player_id):
        player_king_cell = self.get_player_position(player_id)
        friend_king_cell = self.get_player_position(self.get_friend_by_id(player_id))
        for p in self.map.paths:
            first_cell = p.cells[0]
            last_cell = p.cells[len(p.cells) - 1]
            if first_cell == player_king_cell and last_cell == friend_king_cell:
                return p
            if last_cell == player_king_cell and first_cell == friend_king_cell:
                p.cells.reverse()
                return p

    def get_map_row_num(self):
        return self.map.row_count

    def get_map_col_num(self):
        return self.map.column_count

    # return a list of paths crossing one cell
    def get_paths_crossing_cell(self, cell):
        paths = []
        for p in self.map.paths:
            if cell in p.cells:
                paths.append(p)
        return paths

    # return units of player that are currently in map
    def get_player_units(self, player_id):
        player = self.get_player_by_id(player_id)
        return player.units

    # return a list of units in a cell
    def get_cell_units(self, cell):
        return cell.units

    # return the shortest path from player_id fortress to cell
    # this path is in the available path list
    # path may cross from friend
    def get_shortest_path_to_cell(self, player_id, cell):
        shortest_path_to_cell = self.shortest_path.get(player_id)
        if shortest_path_to_cell[cell.row][cell.col] == -1:
            return None
        return shortest_path_to_cell[cell.row][cell.col]

    # returns the limit of ap for each player
    def get_max_ap(self):
        return self.game_constants.max_ap

    # get remaining ap
    def get_remaining_ap(self):
        return self.player.ap

    # returns a list of units in hand
    def get_hand(self):
        return self.player.hand

    # returns a list of units in deck
    def get_deck(self):
        return self.player.deck

    # place unit with type_id in path_id
    def put_unit(self, type_id, path_id):
        e = Event("putUnit", [type_id, path_id])
        self.queue.put(e)

    # Todo put unit

    # return the number of turns passed
    def get_current_turn(self):
        return self.current_turn

    # return the limit of turns
    def get_max_turns(self):
        return self.game_constants.max_turns

    # return the time left to pick units and put in deck in the first turn
    def get_pick_timeout(self):
        return self.game_constants.pick_timeout

    # a constant limit for each turn
    def get_turn_timeout(self):
        return self.game_constants.turn_timeout

    # returns the time left for turn (miliseconds)
    def get_remaining_time(self, ):
        return self.get_turn_timeout() - self.get_time_past()

    # returns the health point remaining for each player
    def get_player_hp(self, player_id):
        player = self.get_player_by_id(player_id)
        return player.king.hp

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
        e = Event("castSpell", [spell.type, [cell.row, cell.col], unit_id, path_id])
        self.queue.put(e)

    # cast spell in the cell 'center'
    def cast_area_spell(self, center=None, row=None, col=None, spell=None, spell_id=None):
        if spell is None:
            spell = self.get_spell_by_type_id(spell_id)
        if row is not None and col is not None:
            e = Event("castSpell", [spell.type, [row, col], -1, -1])
            self.queue.put(e)
        elif center is not None:
            e = Event("castSpell", [spell.type, [center.row, center.col], -1, -1])
            self.queue.put(e)

    # returns a list of units the spell casts effects on
    def get_area_spell_targets(self, center, row=None, col=None, spell=None, spell_id=None):
        if spell is None:
            if spell_id is not None:
                spell = self.get_cast_spell_by_type(spell_id)
        if center is not None:
            pass

    # every once in a while you can upgrade, this returns the remaining time for upgrade
    def get_remaining_turns_to_upgrade(self):
        return self.game_constants.turns_to_upgrade

    # every once in a while a spell is given this remains the remaining time to get new spell
    def get_remaining_turns_to_get_spell(self):
        return self.game_constants.turns_to_spell

    # returns area spells that are casted in last turn and returns other players spells also
    def get_cast_area_spell(self, player_id):
        return [cast_spell_i for cast_spell_i in self.cast_spell.values()
                if cast_spell_i.caster_id and isinstance(cast_spell_i, CastAreaSpell)]

    # returns unit spells that are casted in last turn and returns other players spells also
    def get_cast_unit_spell(self, player_id):
        return [cast_spell_i for cast_spell_i in self.cast_spell.values()
                if cast_spell_i.caster_id and isinstance(cast_spell_i, CastUnitSpell)]

    def get_cast_spells_on_unit(self, unit=None, unit_id=None):
        pass

    # def get_active_poisons_on_unit(self, unit_id=None, unit=None):
    #     temp_unit = unit
    #     if unit_id is not None:
    #         temp_unit = self.get_unit_by_id(unit_id)
    #     if isinstance(temp_unit, Unit):
    #         return temp_unit.active_poisons
    #     return None

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
            self.queue.put(Event("rangeUpgrade", [unit.unit_id]))
        elif unit_id is not None:
            self.queue.put(Event("rangeUpgrade", unit_id))

    def upgrade_unit_damage(self, unit=None, unit_id=None):
        if unit is not None:
            self.queue.put(Event("damageUpgrade", [unit.unit_id]))
        elif unit_id is not None:
            self.queue.put(Event("damageUpgrade", unit_id))

    def get_player_duplicate_unit(self, player_id):
        pass

    def get_player_hasted_units(self, player_id):
        return [unit for unit in self.get_player_by_id(player_id=player_id) if unit.is_hasted > 0]

    def get_player_played_units(self, player_id):
        return [unit for unit in self.get_player_by_id(player_id=player_id) if unit.was_played_this_turn]

    def get_unit_target(self, unit=None, unit_id=None):
        pass

    def get_unit_target_cell(self, unit=None, unit_id=None):
        pass

    def get_king_target(self, player_id):
        pass

    def get_king_target_cell(self, player_id):
        pass

    def get_king_unit_is_attacking_to(self, unit=None, unit_id=None):
        pass

# def get_player_clone_units(self, player_id):
#     return [unit for unit in self.get_player_by_id(player_id=player_id) if unit.is_clone > 0]
#

# def get_player_poisoned_units(self, player_id):
#     return [unit for unit in self.get_player_by_id(player_id=player_id) if unit.active_poisons > 0]
#
