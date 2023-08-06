from pygame import Color

from esp_hadouken.GameChild import *
from esp_hadouken.Font import *

class InputMessage(GameChild):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.render()
        self.set_rect()

    def render(self):
        config = self.get_configuration()
        size = config["ending-input-message-size"]
        text = config["ending-input-message"]
        color = Color(config["ending-input-message-color"])
        background = Color(config["ending-input-message-bg"])
        self.message = Font(self, size).render(text, True, color, background)

    def set_rect(self):
        relative = self.parent.get_rect()
        rect = self.message.get_rect()
        rect.centerx = relative.centerx
        rect.top = self.get_configuration()["ending-input-message-y"]
        self.rect = rect

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def update(self):
        if self.active:
            self.draw()

    def draw(self):
        self.parent.blit(self.message, self.rect)
