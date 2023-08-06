from esp_hadouken import levels

from Road import *

class Void(levels.Void.Void):

    def __init__(self, parent):
        levels.Void.Void.__init__(self, parent)
        self.read_configuration()
        self.road = Road(self)

    def read_configuration(self):
        config = self.get_configuration()
        prefix = "diortem-level-"
        self.padding = config[prefix + "void-padding"]
        self.segment_width_range = config[prefix + "segment-width-range"]
        self.segment_height_range = config[prefix + "segment-height-range"]
        self.shift_range = config[prefix + "shift-range"]
        self.leg_range = config[prefix + "leg-range"]
        self.scroll_speed = config[prefix + "scroll-speed"]

    def update_area(self):
        self.road.update()
