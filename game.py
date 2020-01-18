import copy

from model import CastUnitSpell, CastAreaSpell, Message, Cell
from world import World


class Game(World):

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
            self.queue.put(Message(type="rangeUpgrade", turn=self.get_current_turn()
                                   , info=[unit.unit_id]))
        elif unit_id is not None:
            self.queue.put(Message(type="rangeUpgrade", turn=self.get_current_turn()
                                   , info=unit_id))

    def upgrade_unit_damage(self, unit=None, unit_id=None):
        if unit is not None:
            self.queue.put(Message(type="damageUpgrade", turn=self.get_current_turn(), info={
                "unitId": unit.unit_id
            }))
        elif unit_id is not None:
            self.queue.put(Message(type="damageUpgrade", turn=self.get_current_turn(), info={
                "unitId": unit.unit_id
            }))

    def get_player_duplicate_unit(self, player_id):
        unit_list = []
        for u in self.get_player_by_id(player_id).units:
            if u.is_clone:
                unit_list.append(u)
        return unit_list

    def get_player_hasted_units(self, player_id):
        return [unit for unit in self.get_player_by_id(player_id=player_id).units if unit.is_hasted > 0]

    def get_player_played_units(self, player_id):
        return [unit for unit in self.get_player_by_id(player_id=player_id).units if unit.was_played_this_turn]

    def get_unit_target(self, unit=None, unit_id=None):
        if unit_id is None:
            if unit is None:
                return None
            unit_id = unit.unit_id

        target_id = self.get_unit_by_id(unit_id).target_id
        unit = self.get_unit_by_id(target_id)
        return unit

    def get_unit_target_cell(self, unit=None, unit_id=None):
        if unit_id is None:
            if unit is None:
                return None
            unit_id = unit.unit_id

        target_id = self.get_unit_by_id(unit_id).target_id
        cell = self.get_unit_by_id(unit_id).target_cell
        unit = self.get_unit_by_id(target_id)
        if unit is None:
            return None

        return cell

    def get_king_target(self, player_id):
        king = self.get_player_by_id(player_id).king
        return self.get_unit_by_id(king.target_id)

    def get_king_target_cell(self, player_id):
        king = self.get_player_by_id(player_id).king
        return king.target_cell

    def get_king_unit_is_attacking_to(self, unit=None, unit_id=None):
        if unit is not None:
            unit_id = unit.unit_id
        unit = self.get_unit_by_id(unit_id)
        for p in self.players:
            if unit.target_id == p.player_id:
                return p.player_id
        return -1

    def get_all_base_unit(self):
        return copy.deepcopy(self.base_units)

    def get_all_spells(self):
        return copy.deepcopy(self.spells)

# def get_player_clone_units(self, player_id):
#     return [unit for unit in self.get_player_by_id(player_id=player_id) if unit.is_clone > 0]
#

# def get_player_poisoned_units(self, player_id):
#     return [unit for unit in self.get_player_by_id(player_id=player_id) if unit.active_poisons > 0]
#
