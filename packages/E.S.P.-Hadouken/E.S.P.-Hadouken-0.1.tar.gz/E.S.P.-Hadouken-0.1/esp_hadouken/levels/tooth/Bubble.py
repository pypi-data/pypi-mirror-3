from random import randint
from operator import sub

from pygame import draw

from esp_hadouken.GameChild import *

class Bubble(GameChild):

    def __init__(self, parent, y=None):
        GameChild.__init__(self, parent)
        self.y = y
        self.set_x()

    def set_x(self):
        self.x = self.parent.get_width() / 2

    def update(self):
        self.y += self.parent.scroll_speed
        self.set_radius()

    def set_radius(self):
        parent = self.parent
        radius_range = parent.radius_range
        pos = float(self.y) / -sub(*parent.y_range)
        self.radius = int(pos * -sub(*radius_range) + radius_range[0])

    def draw(self):
        parent = self.parent
        center = self.x, self.y
        draw.circle(parent.area, parent.transparent_color, center, self.radius)
