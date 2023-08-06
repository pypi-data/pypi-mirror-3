from pygame import Surface, Color, Rect

from esp_hadouken.GameChild import *
from esp_hadouken.Font import *

class Controls(Surface, GameChild):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.init_surface()
        self.set_prompt()
        self.set_prompt_rect()
        self.set_rect()
        self.draw()

    def init_surface(self):
        config = self.get_configuration()
        height = config["introduction-controls-height"]
        color = Color(config["introduction-controls-background"])
        Surface.__init__(self, (self.parent.get_width(), height))
        self.fill(color)
        self.set_alpha(config["introduction-controls-alpha"])
        self.bg_color = color

    def set_prompt(self):
        config = self.get_configuration()
        text = config["introduction-controls-text"]
        size = config["introduction-controls-size"]
        color = Color(config["introduction-controls-color"])
        self.prompt = Font(self, size).render(text, True, color, self.bg_color)

    def set_prompt_rect(self):
        rect = self.prompt.get_rect()
        rect.top = (self.get_height() - rect.h) / 2
        rect.left = (self.get_width() - rect.w) / 2
        self.prompt_rect = rect

    def set_rect(self):
        size = self.get_size()
        offset = self.get_configuration()["introduction-controls-offset"]
        y = self.parent.get_height() - size[1] - offset
        self.rect = Rect((0, y), size)

    def draw(self):
        self.blit(self.prompt, self.prompt_rect)
        self.parent.blit(self, self.rect)
