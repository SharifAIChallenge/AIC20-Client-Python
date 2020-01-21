from random import Random


class AI:

    def pick(self, world):
        self.r = Random()
        print("pick")
        world.choose_deck([1, 2, 3, 4])
        print(world.put_unit(type_id=1, path=world.map.paths[self.r.randint(1, 4)]))
        if len(world.player.units) > 0:
            print(world.player.units[0].cell)

    def turn(self, world):
        print("turn")
        if len(world.player.units) > 0:
            print(world.player.units[0].cell)
