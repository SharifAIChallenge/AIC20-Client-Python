class AI:

    def pick(self, world):
        print("pick")
        #self.path_to_friend_check(world)
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

    def turn(self, world):
        print("turn")
        if world.get_current_turn() == 12:
            print("turn 12 baby!")
            print(len(world.get_me().get_spells()))
            for spell in world.get_me().get_spells():
                print(spell)
                print(world.get_me().get_spell_count(spell))
                print("---")

        if world.get_current_turn() == 20:
            print("its turn 2!!!")
            world.put_unit(base_unit=world.get_me().hand[0], path=world.get_me().paths_from_player[0])

