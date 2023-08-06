from pygame import image

from esp_hadouken.GameChild import *

class Exit(GameChild):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.load_image()
        self.set_rect()

    def load_image(self):
        img = image.load(self.get_resource("level-exit-path")).convert()
        img.set_alpha(self.get_configuration()["level-exit-alpha"])
        self.img = img

    def set_rect(self):
        rect = self.img.get_rect()
        width, height = self.parent.get_size()
        rect.bottomright = width - 10, height - 8
        self.rect = rect

    def draw(self):
        self.parent.blit(self.img, self.rect)
