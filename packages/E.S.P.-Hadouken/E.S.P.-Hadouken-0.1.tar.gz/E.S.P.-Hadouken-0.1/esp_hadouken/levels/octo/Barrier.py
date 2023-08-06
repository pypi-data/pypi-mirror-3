from random import randint

from pygame import Surface, Color, Rect

from esp_hadouken.GameChild import *

class Barrier(GameChild, Surface):

    transparent_color = Color("magenta")

    def __init__(self, parent, y=0):
        GameChild.__init__(self, parent)
        Surface.__init__(self, (parent.frame_width, parent.barrier_height))
        self.set_colorkey(self.transparent_color)
        self.convert()
        self.y = y
        self.set_gap()

    def set_gap(self):
        gap = Surface(self.get_size())
        gap.fill(self.transparent_color)
        self.gap_center = randint(0, self.get_width())
        self.gap = gap.convert()

    def update(self):
        self.y += self.parent.scroll_speed
        self.blit_gap()
        self.draw()

    def blit_gap(self):
        gap = self.gap
        width = self.calculate_width()
        position = (self.gap_center - width / 2, 0)
        area = Rect(0, 0, width, gap.get_height())
        self.blit(gap, position, area)
        self.blit_overflow(width, position[0])

    def calculate_width(self):
        y_range = self.parent.y_range
        ratio = (self.y - y_range[0]) / float(y_range[1] - y_range[0])
        min_gap = self.parent.min_gap
        return int(min_gap + (self.get_width() - min_gap) * ratio)

    def blit_overflow(self, width, x):
        gap = self.gap
        frame_width = self.parent.frame_width
        if x < 0 or x + width > frame_width:
            if x < 0:
                overflow = 0 - x
                position = (frame_width - overflow, 0)
            else:
                overflow = x + width - frame_width
                position = (0, 0)
            self.blit(gap, position, Rect(0, 0, overflow, self.get_height()))

    def draw(self):
        self.parent.blit(self, (0, self.y))
