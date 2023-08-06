from random import randint
from operator import sub

from pygame import draw

from esp_hadouken.GameChild import *

class Wave(GameChild):

    def __init__(self, parent, orientation, bottom):
        GameChild.__init__(self, parent)
        self.orientation = orientation
        self.bottom = bottom
        self.edge = 0 if orientation == parent.orient_left else \
                    parent.get_width()
        self.set_base_length()
        self.update()

    def set_base_length(self):
        self.base_length = randint(*self.parent.parent.base_range)

    def get_top(self):
        return self.vertices[0][1]

    def get_bottom(self):
        return self.vertices[1][1]

    def update(self):
        self.bottom += self.parent.parent.scroll_speed
        self.set_height()
        self.set_vertices()
        self.draw()

    def get_pos(self):
        return float(self.bottom) / self.parent.get_height()

    def set_height(self):
        height_r = self.parent.parent.height_range
        self.height = self.get_pos() * -sub(*height_r) + height_r[0]

    def set_vertices(self):
        height = self.height
        edge = self.edge
        base_length = self.base_length
        bottom = self.bottom
        peak_x = height if self.orientation == self.parent.orient_left else \
                 edge - height
        base_top = edge, bottom - base_length
        base_bottom = edge, bottom
        peak = peak_x, bottom - base_length / 2
        self.vertices = base_top, base_bottom, peak

    def draw(self):
        parent = self.parent
        draw.polygon(parent, parent.parent.opaque_color, self.vertices)
