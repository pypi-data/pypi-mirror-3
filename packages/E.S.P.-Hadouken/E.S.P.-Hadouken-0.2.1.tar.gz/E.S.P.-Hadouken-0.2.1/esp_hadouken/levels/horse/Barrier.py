from random import randint
from operator import sub

from pygame import Surface

from esp_hadouken.GameChild import *

class Barrier(GameChild, Surface):

    dir_r, dir_l = 1, -1

    def __init__(self, parent, y, sibling=None):
        GameChild.__init__(self, parent)
        self.y = y
        self.sibling = sibling
        self.init_surface()

    def init_surface(self):
        size = self.determine_size()
        Surface.__init__(self, (size, size))
        self.fill(self.parent.transparent_color)
        self.set_rect()

    def determine_size(self):
        parent = self.parent
        size_range = parent.size_range
        pos = float(self.y) / -sub(*parent.y_range)
        return pos * -sub(*size_range) + size_range[0]

    def set_rect(self):
        rect = self.get_rect()
        rect.top = self.y
        sibling = self.sibling
        if not sibling:
            growth = self.dir_r
            rect.top = self.y
            rect.left = self.generate_initial_x()
        else:
            growth = sibling.growth
            if growth == self.dir_r:
                rect.left = sibling.rect.right
                if rect.right > self.parent.get_width():
                    growth = self.dir_l
                    rect.right = sibling.rect.left
            if growth == self.dir_l:
                rect.right = sibling.rect.left
                if rect.left < 0:
                    growth = self.dir_r
                    rect.left = sibling.rect.right
        self.growth = growth
        self.rect = rect
        self.x = rect.left
        self.set_heading()
        self.set_step()

    def generate_initial_x(self):
        parent = self.parent
        return randint(0, parent.get_width() - parent.size_range[0])

    def set_heading(self):
        if self.rect.centerx > self.parent.get_width() / 2:
            heading = self.dir_l
        else:
            heading = self.dir_r
        self.heading = heading

    def set_step(self):
        parent = self.parent
        center = parent.get_width() / 2
        rnge = abs((self.rect.centerx - center) * 2)
        self.step = float(rnge) / parent.step_limit

    def toggle_heading(self):
        heading = self.heading
        if heading == self.dir_l:
            heading = self.dir_r
        else:
            heading = self.dir_l
        self.heading = heading

    def update(self):
        self.move()
        self.draw()

    def move(self):
        self.x += self.heading * self.step
        self.rect.left = self.x
        
    def draw(self):
        self.parent.area.blit(self, self.rect)
