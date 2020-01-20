class AI:

    def pick(self, world):
        print("pick")
        world.choose_deck([1, 2, 3, 4])
        print(world.get_shortest_path_to_cell(player_id=world.get_my_id(), row=10, col=10))

    def turn(self, world):
        print("turn")
