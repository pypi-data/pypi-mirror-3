from pygame import display, image

from GameChild import *

class Display(GameChild):

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.set_screen()
        self.set_caption()
        self.set_icon()

    def set_screen(self):
        configuration = self.get_configuration()
        self.screen = display.set_mode(configuration["display-dimensions"])

    def set_caption(self):
        display.set_caption(self.get_configuration()["game-title"])

    def set_icon(self):
        path = self.get_resource("display-icon-path")
        display.set_icon(image.load(path).convert_alpha())

    def get_screen(self):
        return self.screen

    def get_size(self):
        return self.screen.get_size()
