from pygame import Surface, Color, Rect

from esp_hadouken.GameChild import GameChild

class Void(Surface, GameChild):

    transparent_color = Color("magenta")
    opaque_color = Color("black")

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        Surface.__init__(self, parent.get_size())
        self.set_colorkey(self.transparent_color)
        self.set_background()

    def set_background(self):
        bg = Surface(self.parent.get_clip().size)
        bg.fill(self.transparent_color)
        self.background = bg.convert()

    def update(self):
        self.set_clip()
        self.clear()
        self.update_area()
        self.draw()

    def set_clip(self):
        Surface.set_clip(self, self.parent.get_clip())

    def clear(self):
        self.blit(self.background, self.get_clip())

    def update_area(self):
        pass

    def draw(self):
        clip = self.get_clip()
        self.parent.blit(self, clip, clip)
