from esp_hadouken.sprite.Sprite import *
from esp_hadouken.GameChild import *

class Diortem(Sprite):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.init_sprite()

    def init_sprite(self):
        configuration = self.get_configuration()
        image_path = self.get_resource("diortem-image-path")
        Sprite.__init__(self, self.parent, image_path, self.parent)
