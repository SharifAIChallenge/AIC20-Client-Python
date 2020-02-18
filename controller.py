import os
import sys
import threading
import traceback
from queue import Queue
from threading import Thread

from AI import AI
from model import Message
from model import ServerConstants
from network import Network
from world import World


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

    # change with switcher
    def handle_message(self, message):
        if message[ServerConstants.KEY_TYPE] == ServerConstants.MESSAGE_TYPE_INIT:
            self.world._handle_init_message(message[ServerConstants.KEY_INFO])
            new_world = World(world=self.world)
            threading.Thread(target=self.launch_on_thread, args=(self.client.pick, new_world)).start()

        elif message[ServerConstants.KEY_TYPE] == ServerConstants.MESSAGE_TYPE_TURN:
            new_world = World(world=self.world)
            new_world._handle_turn_message(message[ServerConstants.KEY_INFO])
            threading.Thread(target=self.launch_on_thread, args=(self.client.turn, new_world)).start()


        elif message[ServerConstants.KEY_TYPE] == ServerConstants.MESSAGE_TYPE_SHUTDOWN:
            new_world = World(world=self.world)
            new_world._handle_turn_message(message[ServerConstants.KEY_INFO]["turnMessage"])
            scores_map = new_world._handle_end_message(message[ServerConstants.KEY_INFO]["scores"])
            self.client.end(new_world, scores_map)
            self.terminate()

    def launch_on_thread(self, action, world):
        try:
            action(world)
        except Exception as e:
            print("Error in client:")
            traceback.print_exc()
            # print(e)
        world._queue.put(Message(type=ServerConstants.MESSAGE_TYPE_END_TURN, turn=world.get_current_turn(), info={}))

    def start(self):
        self.read_settings()
        self.network = Network(ip=self.conf[self.argNames[0]],
                               port=int(self.conf[self.argNames[1]]),
                               token=self.conf[self.argNames[2]],
                               message_handler=self.handle_message)
        self.network.connect()

        def run():
            while self.sending_flag:
                message = self.queue.get()
                self.queue.task_done()

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


if __name__ == '__main__':
    c = Controller()
    if len(sys.argv) > 1 and sys.argv[1] == '--verbose':
        World.DEBUGGING_MODE = True
    c.start()
