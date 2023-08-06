from random import randint

from pygame import Color, Surface

from esp_hadouken import levels
from Bubble import *

class Void(levels.Void.Void):

    def __init__(self, parent):
        levels.Void.Void.__init__(self, parent)
        self.iterations = 0
        self.read_configuration()
        self.set_area()
        self.show()

    def read_configuration(self):
        config = self.get_configuration()
        self.switch_frequency = config["tooth-level-switch-frequency"]
        self.scroll_speed = config["tooth-level-scroll-speed"]
        self.padding = config["tooth-level-void-padding"]
        self.radius_range = config["tooth-level-radius-range"]
        self.spawn_range = config["tooth-level-spawn-range"]

    def set_area(self):
        self.set_y_range()
        y_range = self.y_range
        height = y_range[1] - y_range[0]
        area = Surface((self.parent.get_width(), height)).convert()
        self.area_bg = Surface(area.get_size()).convert()
        self.area = area
        self.generate_bubbles()

    def set_y_range(self):
        padding = self.padding
        parent = self.parent
        start = parent.bandit.rect.bottom + padding[0]
        end = parent.get_height() - padding[1]
        self.y_range = start, end

    def generate_bubbles(self):
        self.bubbles = []
        y = self.get_height()
        while y > -self.radius_range[0]:
            self.add_bubble(y)
            y -= self.next_spawn + self.radius_range[0]

    def add_bubble(self, y=None):
        if y is None:
            y = -self.radius_range[0]
        self.bubbles.insert(0, Bubble(self, y))
        self.next_spawn = randint(*self.spawn_range)

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def update_area(self):
        self.update_bubbles()
        iterations = self.iterations + 1
        if 1.0 / iterations <= self.switch_frequency:
            self.toggle()
            iterations = 0
        if self.visible:
            self.clear_area()
            self.draw_area()
        self.iterations = iterations

    def update_bubbles(self):
        bubbles = self.bubbles
        radius_range = self.radius_range
        if bubbles[0].y - radius_range[0] > self.next_spawn:
            self.add_bubble()
        for bubble in bubbles:
            if bubble.y > self.y_range[1] + radius_range[1]:
                bubbles.remove(bubble)
            else:
                bubble.update()

    def clear_area(self):
        self.area.blit(self.area_bg, (0, 0))

    def draw_area(self):
        self.draw_bubbles()
        self.blit(self.area, (0, self.y_range[0]))

    def draw_bubbles(self):
        for bubble in self.bubbles:
            bubble.draw()
