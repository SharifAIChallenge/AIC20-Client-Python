class AI:

    def pick(self, world):
        print("pick")
        world.choose_deck([1, 2, 3, 4])
        for i in world.base_units:
            print(i.type_id)
        for i in world.spells:
            print(i.type_id)

    def turn(self, world):
        print("turn")
