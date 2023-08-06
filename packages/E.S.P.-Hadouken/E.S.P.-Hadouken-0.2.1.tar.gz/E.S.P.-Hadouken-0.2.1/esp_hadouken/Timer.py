from time import time

from pygame.locals import *

from GameChild import *
from Input import *

class Timer(GameChild, dict):

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.subscribe_to_events()
        self.reset()

    def subscribe_to_events(self):
        self.subscribe_to(Input.command_event, self.respond_to_event)

    def respond_to_event(self, event):
        if event.command == "reset":
            self.reset()

    def reset(self):
        self.clear_current_interval()
        self.concealed = False
        dict.__init__(self, {"octo": 0, "horse": 0, "diortem": 0, "circulor": 0,
                             "tooth": 0})

    def clear_current_interval(self):
        self.start_time = None
        self.pause_length = 0
        self.pause_start_time = None
        self.paused = False
        self.current_level = None

    def start(self, level):
        self.start_time = time()
        self.current_level = level

    def pause(self):
        if self.start_time:
            paused = self.paused
            if self.paused:
                self.pause_length += time() - self.pause_start_time
            else:
                self.pause_start_time = time()
            self.paused = not paused

    def stop(self):
        start = self.start_time
        level = self.current_level
        if None not in (start, level):
            interval = time() - start - self.pause_length
            self[level] += interval
        self.clear_current_interval()

    def total(self):
        if self.concealed:
            return self.get_configuration()["timer-max-time"]
        return sum(self.values())

    def conceal(self):
        self.concealed = True
