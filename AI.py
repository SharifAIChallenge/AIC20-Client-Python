class AI:

    def pick(self, world):
        print("pick")
        world.choose_deck([1, 2, 3 , 4])
        print("this is the position")
        print(world.get_player_position(world.get_my_id()).row)

    def turn(self, world):
        print("turn")
