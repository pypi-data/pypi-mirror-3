from pygame import Surface, Color
from pygame.locals import *

from esp_hadouken.GameChild import *
from esp_hadouken.Font import *

class Cell(GameChild, Surface):

    def __init__(self, parent, index):
        GameChild.__init__(self, parent)
        self.index = index
        self.init_surface()
        self.reset()

    def __str__(self):
        return chr(self.char).upper()

    def init_surface(self):
        size = self.get_configuration()["scoreboard-prompt-dimensions"]
        margin = self.get_margin()
        width = size[0] / self.parent.cell_count - margin
        Surface.__init__(self, (width, size[1]))
        rect = self.get_rect()
        rect.left = (self.get_width() + margin) * self.index + margin / 2
        self.rect = rect

    def get_margin(self):
        return self.get_configuration()["scoreboard-prompt-margin"]

    def reset(self):
        self.set_char(self.get_blank_char())

    def get_blank_char(self):
        return ord(self.get_configuration()["scoreboard-prompt-blank-char"])

    def set_char(self, char):
        self.char = char
        self.set_color()
        self.draw()

    def set_color(self):
        char = self.char
        if char == self.get_blank_char():
            color = Color(
                self.get_configuration()["scoreboard-prompt-blank-color"])
        else:
            color = self.get_glyph_palette()[char - K_a]
        self.color = color

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def draw(self):
        self.fill(self.color)
        self.render_char()
        self.parent.blit(self, self.rect)

    def render_char(self):
        config = self.get_configuration()
        size = config["scoreboard-prompt-text-size"]
        color = Color(config["scoreboard-prompt-text-color"])
        text = Font(self, size).render(str(self), True, color)
        rect = text.get_rect()
        rect.center = self.get_rect().center
        self.blit(text, rect)

    def is_blank(self):
        return self.char == self.get_blank_char()
