from pygame import Surface, Rect

from esp_hadouken.GameChild import *
from Wave import *

class Waves(GameChild, Surface):

    orient_left, orient_right = range(2)

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.init_surface()
        self.set_background()
        self.generate_waves()

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
        background.fill(self.parent.transparent_color)
        background.convert()
        self.background = background

    def generate_waves(self):
        self.waves = waves = []
        while not waves or waves[0].get_bottom() < 0:
            self.add_wave()

    def add_wave(self):
        waves = self.waves
        if not waves:
            bottom = self.get_height()
            orientation = self.orient_right
        else:
            bottom = waves[0].get_top()
            orientation = not waves[0].orientation
        waves.insert(0, Wave(self, orientation, bottom))

    def update(self):
        self.set_clip()
        self.clear()
        self.update_waves()
        self.draw()

    def set_clip(self):
        parent = self.parent
        y = parent.get_clip().top - parent.padding[0] - \
            parent.parent.bandit.rect.h
        Surface.set_clip(self, Rect((0, y), parent.get_clip().size))

    def clear(self):
        self.blit(self.background, (0, 0))

    def update_waves(self):
        waves = self.waves
        if waves[0].get_bottom() > 0:
            self.add_wave()
        for wave in waves:
            if wave.get_top() > self.get_height():
                waves.remove(wave)
            else:
                wave.update()

    def draw(self):
        self.parent.blit(self, self.rect)
