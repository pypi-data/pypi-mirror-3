from operator import sub
from random import randint

from pygame import Surface, Rect, Color, transform, draw

from esp_hadouken.GameChild import *

class Segment(GameChild):

    def __init__(self, parent, leg, bottom, x):
        GameChild.__init__(self, parent)
        self.init_rect(leg, bottom, x)
        self.color = parent.parent.transparent_color

    def init_rect(self, leg, bottom, x):
        parent = self.parent
        rect = Rect(0, 0, 0, randint(*parent.parent.segment_height_range))
        x_range = parent.x_range
        if x is None:
            x = randint(*x_range)
        else:
            x += leg.direction * randint(*parent.parent.shift_range)
        if x < x_range[0] or x > x_range[1]:
            leg.change_direction()
            if x < x_range[0]:
                x = x_range[0]
            else:
                x = x_range[1]
        rect.centerx = x
        rect.bottom = bottom
        self.rect = rect

    def update(self):
        self.update_width()
        self.recenter()
        self.scroll()
        self.draw()

    def update_width(self):
        parent = self.parent
        rect = self.rect
        pos = float(rect.bottom) / parent.get_height()
        centerx = rect.centerx
        width_r = parent.parent.segment_width_range
        rect.w = pos * -sub(*width_r) + width_r[0]
        rect.centerx = centerx

    def recenter(self):
        rect = self.rect
        right_bound = self.parent.get_width()
        if rect.left < 0:
            rect.left = 0
        elif rect.right > right_bound:
            rect.right = right_bound

    def scroll(self):
        self.rect.top += self.parent.parent.scroll_speed

    def draw(self):
        draw.rect(self.parent, self.color, self.rect)
