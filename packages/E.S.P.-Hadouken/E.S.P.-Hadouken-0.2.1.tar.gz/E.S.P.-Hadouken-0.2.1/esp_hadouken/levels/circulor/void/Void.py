from esp_hadouken import levels

from Waves import *

class Void(levels.Void.Void):

    def __init__(self, parent):
        levels.Void.Void.__init__(self, parent)
        self.read_configuration()
        self.waves = Waves(self)

    def read_configuration(self):
        config = self.get_configuration()
        prefix = "circulor-level-"
        self.height_range = config[prefix + "height-range"]
        self.base_range = config[prefix + "base-range"]
        self.scroll_speed = config[prefix + "scroll-speed"]
        self.padding = config[prefix + "void-padding"]

    def update_area(self):
        self.waves.update()
