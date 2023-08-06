from pygame import image

from GameChild import *

class PauseScreen(GameChild):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.load_image()

    def load_image(self):
        self.img = image.load(self.get_resource("pause-image-path"))

    def show(self):
        self.get_screen().blit(self.img, (0, 0))
