from esp_hadouken.levels.Level import *
from void.Void import *

class Circulor(Level):

    def __init__(self, parent):
        Level.__init__(self, parent)

    def set_dot(self):
        bounds = (0, self.get_width()), (0, self.get_height())
        wrap = False, False
        dot = Dot(self, bounds, wrap)
        self.dot = dot

    def set_void(self):
        self.void = Void(self)
