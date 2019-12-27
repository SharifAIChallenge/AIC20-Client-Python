import os
import threading
from queue import Queue
from threading import Thread

from AI import AI
from model import Event
from model import ServerConstants
from network import Network
from world import World


class GameConstants:
    def __init__(self, max_ap, max_turns, turn_timeout, pick_timeout,
                 turns_to_upgrade, turns_to_spell, damage_upgrade_addition, range_upgrade_addition):
        self.max_ap = max_ap
        self.max_turns = max_turns
        self.turn_timeout = turn_timeout
        self.pick_timeout = pick_timeout
        self.turns_to_upgrade = turns_to_upgrade
        self.turns_to_spell = turns_to_spell
        self.damage_upgrade_addition = damage_upgrade_addition
        self.range_upgrade_addition = range_upgrade_addition
        if World.DEBUGGING_MODE:
            import datetime
            World.LOG_FILE_POINTER = open('client' + '-' +
                                          datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f") + '.log', 'w+')


class Controller:
    def __init__(self):
        self.sending_flag = True
        self.conf = {}
        self.network = None
        self.queue = Queue()
        self.world = World(queue=self.queue)
        self.client = AI()
        self.argNames = ["AICHostIP", "AICHostPort", "AICToken", "AICRetryDelay"]
        self.argDefaults = ["127.0.0.1", 7099, "00000000000000000000000000000000", "1000"]
        self.turn_num = 0

    #change with switcher
    def handle_message(self, message):
        if message[ServerConstants.KEY_NAME] == ServerConstants.MESSAGE_TYPE_INIT:
            self.world._handle_init_message(message)

        elif message[ServerConstants.KEY_NAME] == ServerConstants.MESSAGE_TYPE_PICK:
            new_world = World(world=self.world)
            new_world._handle_pick_message(message)
            threading.Thread(target=self.launch_on_thread, args=(self.client.pick, 'pick', new_world,
                                                                 [new_world.current_turn])).start()

        elif message[ServerConstants.KEY_NAME] == ServerConstants.MESSAGE_TYPE_TURN:
            new_world = World(world=self.world)
            new_world._handle_turn_message(message)
            threading.Thread(target=self.launch_on_thread, args=(self.client.turn, 'turn', new_world,
                                                                     [new_world.current_turn])).start()

        elif message[ServerConstants.KEY_NAME] == ServerConstants.MESSAGE_TYPE_SHUTDOWN:
            self.terminate()

    def launch_on_thread(self, action, name, new_world, args):
        try:
            action(new_world)
        except Exception as e:
            print(e)
        new_world.queue.put(Event(name + '-end', args))

    def start(self):
        self.read_settings()
        self.network = Network(ip=self.conf[self.argNames[0]],
                               port=int(self.conf[self.argNames[1]]),
                               token=self.conf[self.argNames[2]],
                               message_handler=self.handle_message)
        self.network.connect()

        def run():
            while self.sending_flag:
                event = self.queue.get()
                self.queue.task_done()
                message = {
                    'name': Event.EVENT,
                    'args': [{'type': event.type, 'args': event.args}]
                }
                if World.DEBUGGING_MODE and World.LOG_FILE_POINTER is not None:
                    World.LOG_FILE_POINTER.write('------send message to server-----\n ' + message.__str__())
                self.network.send(message)

        Thread(target=run, daemon=True).start()

    def read_settings(self):
        if os.environ.get(self.argNames[0]) is None:
            for i in range(len(self.argNames)):
                self.conf[self.argNames[i]] = self.argDefaults[i]
        else:
            for i in range(len(self.argNames)):
                self.conf[self.argNames[i]] = os.environ.get(self.argNames[i])

    def terminate(self):
        if World.LOG_FILE_POINTER is not None:
            World.LOG_FILE_POINTER.write('finished')
            World.LOG_FILE_POINTER.flush()
            World.LOG_FILE_POINTER.close()
        print("finished!")
        self.network.close()
        self.sending_flag = False
