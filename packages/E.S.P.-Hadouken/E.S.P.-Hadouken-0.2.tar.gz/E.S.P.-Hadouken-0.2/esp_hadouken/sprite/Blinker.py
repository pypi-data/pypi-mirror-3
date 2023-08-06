from random import choice

from pygame import Color, PixelArray

from esp_hadouken.GameChild import *

class Blinker(GameChild):
    
    def __init__(self, sprite, initial_freq, max_freq):
        GameChild.__init__(self, sprite)
        self.sprite = sprite
        self.frequency = initial_freq
        self.max_freq = max_freq
        self.iterations = 0
        self.set_palettes()

    def set_palettes(self):
        configuration = self.get_configuration()
        self.inner_palette = map(
            self.translate_hex_color, configuration["sprite-inner-palette"])
        self.outer_palette = map(
            self.translate_hex_color, configuration["sprite-outer-palette"])
        self.palette = (Color("black"), Color("white"))

    def translate_hex_color(self, color):
        return Color(color + "ff")

    def build_palette(self):
        return (choice(self.inner_palette), choice(self.outer_palette))

    def paint(self):
        image = self.sprite.image
        pixels = PixelArray(image)
        old_palette = self.palette
        new_palette = self.build_palette()
        pixels.replace(old_palette[0], new_palette[0])
        pixels.replace(old_palette[1], new_palette[1])
        self.palette = new_palette
        image.unlock()

    def blink(self):
        iterations = self.iterations + 1
        if 1.0 / iterations <= self.frequency:
            self.paint()
            iterations = 0
        self.iterations = iterations
