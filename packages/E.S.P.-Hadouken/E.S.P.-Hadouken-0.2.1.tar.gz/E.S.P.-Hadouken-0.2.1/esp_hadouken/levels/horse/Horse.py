from esp_hadouken.levels.Level import *
from Gauntlet import *

class Horse(Level):

    def __init__(self, parent):
        Level.__init__(self, parent)

    def set_void(self):
        self.void = Gauntlet(self)
