class AI:

    def pick(self, world):
        print("pick")
        world.choose_deck([1, 2, 3, 4])
        print(world.get_player_by_id(world.get_my_id()))
        print(world.get_player_by_id(world.get_friend_id()))
        for p in world.map.paths:
            print(p)
            print("------------")

        print(world.get_path_to_friend(world.get_my_id()))

    def turn(self, world):
        print("turn")
