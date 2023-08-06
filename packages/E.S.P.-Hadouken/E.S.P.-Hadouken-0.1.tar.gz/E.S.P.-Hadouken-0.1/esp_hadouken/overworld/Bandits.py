from os import listdir
from os.path import join, basename
from re import match

from esp_hadouken.GameChild import *
from esp_hadouken.sprite.Sprite import *

class Bandits(GameChild, list):

    def __init__(self, overworld):
        GameChild.__init__(self, overworld)
        self.set_y()
        self.add_bandits()
        self.arrange()

    def __iter__(self):
        return self.bandits.__iter__()

    def set_y(self):
        margin = self.get_configuration()["overworld-bandits-margin"]
        self.y = self.parent.wall.get_bottom() + margin
        self.margin = margin

    def add_bandits(self):
        bandits = []
        path = self.get_resource("overworld-bandits-path")
        for name in sorted(listdir(path)):
            bandits.append(Bandit(self, join(path, name), self.parent))
        self.bandits = bandits

    def arrange(self):
        bandits = self.bandits
        count = self.count_visible()
        bandit_width = bandits[0].rect.w
        margin = self.margin
        group_width = bandit_width * count + margin * (count - 1)
        start = (self.parent.get_width() - group_width) / 2
        for ii, bandit in enumerate(filter(lambda x: x.visible, bandits)):
            bandit.place(start + (ii * (bandit.rect.w + margin)), self.y)

    def count_visible(self):
        count = 0
        for bandit in self:
            count += bandit.visible
        return count

    def reset(self):
        for bandit in self:
            bandit.show()
        self.arrange()

    def update(self):
        for bandit in self:
            bandit.update()

    def remove(self, name):
        for bandit in self:
            if bandit.name == name:
                bandit.hide()
                break
        self.arrange()
        

class Bandit(Sprite):

    def __init__(self, parent, path, display_surface):
        Sprite.__init__(self, parent, path, display_surface)
        self.set_name()
        self.set_color()

    def set_name(self):
        pattern = ".*\_(.*)\..*"
        self.name = match(pattern, self.image_path).groups()[0]

    def set_color(self):
        self.color = self.image.get_at((0, 0))
