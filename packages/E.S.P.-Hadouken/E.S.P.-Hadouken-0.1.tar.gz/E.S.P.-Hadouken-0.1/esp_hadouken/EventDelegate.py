import pygame
from pygame.locals import *

from GameChild import *

class EventDelegate(GameChild):

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.subscribers = dict()
        self.disable()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def dispatch_events(self):
        if self.enabled:
            subscribers = self.subscribers
            for event in pygame.event.get():
                kind = event.type
                if kind in subscribers:
                    for subscriber in subscribers[kind]:
                        subscriber(event)
        else:
            pygame.event.pump()

    def add_subscriber(self, kind, callback):
        subscribers = self.subscribers
        if kind not in subscribers:
            subscribers[kind] = list()
        subscribers[kind].append(callback)

    def remove_subscriber(self, kind, callback):
        self.subscribers[kind].remove(callback)
