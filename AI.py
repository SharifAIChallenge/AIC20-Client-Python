class AI:

    def pick(self, world):
        # path check:
        print("pick")
        world.choose_deck([1, 2, 3, 4])
        print(world.get_me())
        print(world.get_me().path_to_friend)
        print("----------")
        print(world.get_friend())
        print(world.get_friend().path_to_friend)
        print("----------")
        print(world.get_first_enemy())
        print(world.get_first_enemy().path_to_friend)
        print("----------")
        print(world.get_second_enemy())
        print(world.get_second_enemy().path_to_friend)

    def turn(self, world):
        print("turn")
