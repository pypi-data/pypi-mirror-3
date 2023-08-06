from random import randint

from pygame import Surface

from esp_hadouken import levels
from Barrier import *

class Void(levels.Void.Void):

    def __init__(self, parent):
        levels.Void.Void.__init__(self, parent)
        self.frame_width = self.parent.get_width()
        self.read_configuration()
        self.init_barriers()

    def read_configuration(self):
        config = self.get_configuration()
        self.barrier_height = config["octo-level-barrier-height"]
        self.min_gap = config["octo-level-min-gap"]
        self.spawn_range = config["octo-level-spawn-range"]
        self.void_padding = config["octo-level-void-padding"]
        self.scroll_speed = config["octo-level-scroll-speed"]

    def init_barriers(self):
        self.set_y_range()
        y_range = self.y_range
        y = y_range[0]
        barriers = []
        y = self.generate_spawn_distance()
        while y < y_range[1]:
            barriers.append(Barrier(self, y))
            y += self.generate_spawn_distance()
        self.barriers = barriers
        self.next_spawn = self.generate_spawn_distance()

    def set_y_range(self):
        padding = self.void_padding
        parent = self.parent
        start = parent.bandit.rect.bottom + padding[0]
        end = parent.get_height() - padding[1]
        self.y_range = start, end

    def generate_spawn_distance(self):
        return randint(*self.spawn_range)

    def update_area(self):
        barriers = self.barriers
        if barriers[0].y - self.y_range[0] > self.next_spawn:
            barriers.insert(0, Barrier(self, self.y_range[0]))
            self.next_spawn = self.generate_spawn_distance()
        for barrier in barriers:
            if barrier.y > self.y_range[1]:
                barriers.remove(barrier)
            else:
                barrier.update()
