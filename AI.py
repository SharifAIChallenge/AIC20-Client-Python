class AI:
    # this function is called in the beginning for deck picking and pre process
    def pick(self, world):
        print("pick")
        # self.path_to_friend_check(world)
        world.choose_deck([1, 2, 3, 4])

    def path_to_friend_check(self, world):
        # path check:
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

    # it is called every turn for doing process during the game
    def turn(self, world):
        myp = world.get_me()
        fir = world.get_friend()

        try:
            print(world.get_shortest_path_to_cell(from_player=myp, cell=fir.paths_from_player[0].cells[3]))
        except Exception as e:
            print(e)

        print("turn")

    # it is called after the game ended and it does not affect the game.
    # using this function you can access the result of the game.
    # scores is a map from int to int which the key is player_id and value is player_score
    def end(self, world, scores):
        print("ending")
