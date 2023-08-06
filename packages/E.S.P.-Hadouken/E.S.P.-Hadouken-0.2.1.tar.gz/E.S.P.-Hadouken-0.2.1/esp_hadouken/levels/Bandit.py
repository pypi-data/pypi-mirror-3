from os.path import join

from esp_hadouken.sprite.Sprite import *
from esp_hadouken.GameChild import *

class Bandit(Sprite):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.init_sprite()
        self.place()
        self.show()

    def init_sprite(self):
        name = self.parent.get_name()
        config = self.get_configuration()
        directory = self.get_resource("level-bandit-sprite-path")
        path = join(directory, name + config["image-extension"])
        Sprite.__init__(self, self.parent, path, self.parent)

    def place(self):
        name = self.parent.get_name()
        pos = self.get_configuration()[name + "-level-bandit-position"]
        self.rect.center = pos
