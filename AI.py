import random

from model import *
from world import World


class AI:
    def __init__(self):
        self.rows = 0
        self.cols = 0
        self.path_for_my_units = None

    # this function is called in the beginning for deck picking and pre process
    def pick(self, world: World):
        print("pick started!")

        # pre process
        map = world.get_map()
        self.rows = map.row_num
        self.cols = map.col_num

        # choosing all flying units
        all_base_units = world.get_all_base_units()
        my_hand = [base_unit for base_unit in all_base_units if base_unit.is_flying]

        # picking the chosen hand - rest of the hand will automatically be filled with random base_units
        world.choose_hand(base_units=my_hand)
        # other pre process
        self.path_for_my_units = world.get_friend().paths_from_player[0]

    # it is called every turn for doing process during the game
    def turn(self, world: World):
        print("turn started:", world.get_current_turn())
        myself = world.get_me()
        max_ap = world.get_game_constants().max_ap
        # play all of hand once your ap reaches maximum. if ap runs out, putUnit doesn't do anything
        if myself.ap == max_ap:
            for base_unit in myself.hand:
                world.put_unit(base_unit=base_unit, path=self.path_for_my_units)

        # this code tries to cast the received spell
        received_spell = world.get_received_spell()
        if received_spell is not None:
            if received_spell.is_area_spell():
                if received_spell.target == SpellTarget.ENEMY:
                    enemy_units = world.get_first_enemy().units
                    if len(enemy_units) > 0:
                        world.cast_area_spell(center=enemy_units[0].cell, spell=received_spell)
                elif received_spell.target == SpellTarget.ALLIED:
                    friend_units = world.get_friend().units
                    if len(friend_units) > 0:
                        world.cast_area_spell(center=friend_units[0].cell, spell=received_spell)
                elif received_spell.target == SpellTarget.SELF:
                    my_units = myself.units
                    if len(my_units) > 0:
                        world.cast_area_spell(center=my_units[0].cell, spell=received_spell)
            else:
                my_units = myself.units
                if len(my_units) > 0:
                    unit = my_units[0]
                    my_paths = myself.paths_from_player
                    path = my_paths[random.randint(0, len(my_paths) - 1)]
                    size = len(path.cells)
                    cell = path.cells[int((size - 1) / 2)]
                    world.cast_unit_spell(unit=unit, path=path, cell=cell, spell=received_spell)

        # this code tries to upgrade damage of first unit. in case there's no damage token, it tries to upgrade range
        if len(myself.units) > 0:
            unit = myself.units[0]
            world.upgrade_unit_damage(unit=unit)
            world.upgrade_unit_range(unit=unit)

    # it is called after the game ended and it does not affect the game.
    # using this function you can access the result of the game.
    # scores is a map from int to int which the key is player_id and value is player_score
    def end(self, world: World, scores):
        print("end started!")
        print("My score:", scores[world.get_me().player_id])
