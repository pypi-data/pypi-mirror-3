from random import randint

from pygame import Surface, Color, Rect

from esp_hadouken.GameChild import *
from Segment import *

class Road(GameChild, Surface):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.init_surface()
        self.set_background()
        self.set_x_range()
        self.generate_segments()

    def init_surface(self):
        parent = self.parent
        width = parent.get_width()
        padding = parent.padding
        bandit_height = parent.parent.bandit.rect.h
        height = parent.get_height() - sum(padding) - bandit_height
        rect = Rect(0, padding[0] + bandit_height, width, height)
        Surface.__init__(self, rect.size)
        self.convert()
        self.rect = rect

    def set_background(self):
        background = Surface(self.get_size())
        background.fill(self.parent.opaque_color)
        background.convert()
        self.background = background

    def set_x_range(self):
        max_seg = self.parent.segment_width_range[1]
        self.x_range = max_seg / 2, self.get_width() - max_seg / 2

    def generate_segments(self):
        self.segments = []
        self.leg = Leg(self)
        y = self.get_height()
        while y > 0:
            self.add_segment(y)
            y -= self.segments[0].rect.h

    def add_segment(self, bottom=None):
        leg = self.leg
        segments = self.segments
        if leg.is_complete():
            leg = Leg(self)
        if bottom is None:
            bottom = segments[0].rect.top
        x = segments[0].rect.centerx if segments else 0
        segments.insert(0, Segment(self, leg, bottom, x))
        leg.advance()
        self.leg = leg

    def update(self):
        self.set_clip()
        self.clear()
        self.update_segments()
        self.draw()

    def set_clip(self):
        parent = self.parent
        y = parent.get_clip().top - parent.padding[0] - parent.parent.bandit.rect.h
        Surface.set_clip(self, Rect((0, y), parent.get_clip().size))

    def clear(self):
        self.blit(self.background, (0, 0))

    def update_segments(self):
        if self.segments[0].rect.top >= -self.parent.segment_height_range[1]:
            self.add_segment()
        for segment in self.segments:
            if segment.rect.top > self.get_height():
                self.segments.remove(segment)
            else:
                segment.update()

    def draw(self):
        self.parent.blit(self, self.rect)


class Leg:

    dirs = [-1, 1]

    def __init__(self, road):
        self.road = road
        self.length = randint(*road.parent.leg_range)
        self.direction = self.dirs[randint(0, len(self.dirs) - 1)]
        self.index = 0

    def advance(self):
        self.index += 1
        self.shift = randint(*self.road.parent.shift_range) * self.direction

    def change_direction(self):
        dirs = self.dirs
        direction = self.direction
        if direction == dirs[0]:
            direction = dirs[1]
        else:
            direction = dirs[0]
        self.direction = direction

    def is_complete(self):
        return self.index >= self.length

