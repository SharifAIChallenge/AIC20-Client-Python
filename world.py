

class World:
    def _init_(self):
        pass

    # put unit_id in path_id in position 'index' all spells of one
    def cast_unit_spell(self, unit_id, path_id, index, spell, spell_id):
        pass

    def cast_area_spell(self, center, spell, spell_id):
        pass

    def get_area_spell_targets(self, center, spell, spell_id):
        pass

    def get_remaining_turns_to_upgrade(self):
        pass
