from esp_hadouken.levels.Level import *
from Void import *

class Tooth(Level):

    def __init__(self, parent):
        Level.__init__(self, parent)

    def set_void(self):
        self.void = Void(self)
