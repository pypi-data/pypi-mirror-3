from pygame import Surface, Color

from esp_hadouken.GameChild import *
from esp_hadouken.Font import *

class Distance(GameChild, Surface):

    transparent_color = Color("magenta")

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.init_surface()
        self.set_font()
        self.rect = self.get_rect()

    def init_surface(self):
        Surface.__init__(self, self.get_configuration()["distance-dimensions"])
        self.set_colorkey(self.transparent_color)

    def set_font(self):
        self.font = Font(self, self.get_configuration()["distance-text-size"])

    def place(self):
        self.rect.bottomleft = self.parent.get_clip().bottomleft

    def update(self):
        self.clear()
        self.place()
        self.render_distance()
        self.draw()

    def clear(self):
        self.fill(Color(self.get_configuration()["distance-background-color"]))

    def render_distance(self):
        config = self.get_configuration()
        distance = self.parent.get_distance_to_target()
        text = "%i%s" % (int(distance * config["distance-modifier"]),
                         config["distance-suffix"])
        color = Color(config["distance-text-color"])
        rend = self.font.render(text, True, color)
        rect = rend.get_rect()
        rect.center = self.get_rect().center
        self.blit(rend, rect)

    def draw(self):
        self.parent.blit(self, self.rect)
