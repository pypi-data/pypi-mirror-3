from pygame import Color

from esp_hadouken.GameChild import *

class GlyphPalette(GameChild, list):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        list.__init__(self, [])
        self.set_interval_properties()
        self.populate()

    def set_interval_properties(self):
        length = self.get_configuration()["scoreboard-palette-length"]
        interval_count = 6
        self.interval_length = length / interval_count
        self.overflow = length % interval_count

    def populate(self):
        brightness = self.get_configuration()["scoreboard-palette-brightness"]
        self.add_interval([255, brightness, brightness], [0, 1, 0])
        self.add_interval([255, 255, brightness], [-1, 0, 0])
        self.add_interval([brightness, 255, brightness], [0, 0, 1])
        self.add_interval([brightness, 255, 255], [0, -1, 0])
        self.add_interval([brightness, brightness, 255], [1, 0, 0])
        self.add_interval([255, brightness, 255], [0, 0, -1])

    def add_interval(self, components, actions):
        for ii, action in enumerate(actions):
            if action == 1:
                components[ii] = 0
            elif action == -1:
                components[ii] = 255
        length = self.interval_length + (self.overflow > 0)
        self.overflow -= 1
        step = 255 / length
        for ii in range(length):
            self.append(Color(*components))
            for ii, action in enumerate(actions):
                if action == 1:
                    components[ii] += step
                elif action == -1:
                    components[ii] -= step
