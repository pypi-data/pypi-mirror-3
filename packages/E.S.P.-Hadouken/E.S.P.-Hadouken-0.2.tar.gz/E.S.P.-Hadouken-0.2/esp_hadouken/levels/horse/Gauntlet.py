from random import randint

from pygame import Surface, Color

from esp_hadouken.levels.Void import *
from Barrier import *

class Gauntlet(Void):

    step_count = 0

    def __init__(self, parent):
        Void.__init__(self, parent)
        self.read_configuration()
        self.set_area()
        self.generate_barriers()

    def read_configuration(self):
        config = self.get_configuration()
        prefix = "horse-level-"
        self.padding = config[prefix + "void-padding"]
        self.size_range = config[prefix + "size-range"]
        self.step_limit = config[prefix + "step-limit"]

    def set_area(self):
        self.set_y_range()
        y_range = self.y_range
        height = y_range[1] - y_range[0]
        area = Surface((self.parent.get_width(), height)).convert()
        self.area_bg = Surface(area.get_size()).convert()
        self.area = area

    def set_y_range(self):
        padding = self.padding
        start = self.parent.bandit.rect.h + padding[0]
        end = self.get_height() - padding[1]
        self.y_range = start, end

    def generate_barriers(self):
        self.barriers = barriers = []
        y = 0
        while y < self.area.get_height():
            sibling = None if not barriers else barriers[-1]
            barriers.append(Barrier(self, y, sibling))
            y += barriers[-1].get_height()

    def update_area(self):
        self.update_step_count()
        self.clear_area()
        self.update_barriers()
        self.draw_area()

    def update_step_count(self):
        count = self.step_count + 1
        if count > self.step_limit:
            count = 0
            self.toggle_barrier_headings()
        self.step_count = count

    def toggle_barrier_headings(self):
        for barrier in self.barriers:
            barrier.toggle_heading()

    def clear_area(self):
        self.area.blit(self.area_bg, (0, 0))

    def update_barriers(self):
        for barrier in self.barriers:
            barrier.update()

    def draw_area(self):
        self.blit(self.area, (0, self.y_range[0]))
