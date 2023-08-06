from math import floor
import copy

import pygame

from Blinker import *
from esp_hadouken.GameChild import *

class Sprite(GameChild):

    def __init__(self, parent, image_path, display_surface, bounds=(None, None),
                 wrap=(False, False), initial_blink_freq=0, max_blink_freq=1):
        GameChild.__init__(self, parent)
        self.image_path = image_path
        self.display_surface = display_surface
        self.bounds = bounds
        self.wrap = wrap
        self.restricted_areas = []
        self.blinker = Blinker(self, initial_blink_freq, max_blink_freq)
        self.add_image()
        self.hide()

    def add_image(self):
        image = pygame.image.load(self.image_path).convert_alpha()
        self.rect = image.get_rect()
        self.old_rect = self.rect
        self.image = image

    def paint(self):
        self.blinker.paint()

    def move(self, x=0, y=0):
        self.old_rect = copy.copy(self.rect)
        if type(x) is tuple or type(x) is list:
            x, y = x[0], x[1]
        if x < 0:
            x = floor(x)
        if y < 0:
            y = floor(y)
        rect = self.rect
        self.place(rect.left + x, rect.top + y)
        self.rect = self.accommodate_wrapping(rect)

    def place(self, x=None, y=None):
        rect = self.rect
        if type(x) is tuple or type(x) is list:
            x, y = x[0], x[1]
        if x is None:
            x = rect.left
        if y is None:
            y = rect.top
        self.rect.topleft = x, y

    def accommodate_wrapping(self, rect):
        horizontal, vertical = self.wrap
        scope = self.display_surface.get_rect()
        if vertical:
            if rect.top < -rect.h:
                rect.top += scope.h
            elif rect.top > scope.h:
                rect.top -= scope.h
        if horizontal:
            if rect.left < 0:
                rect.left += scope.w - rect.w - 1
            elif rect.right > scope.w:
                rect.right -= scope.w - rect.w - 1
        return rect

    def add_restricted_areas(self, rects):
        if type(rects) is not list:
            rects = [rects]
        self.restricted_areas += rects

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)

    def resize(self, size):
        self.image = pygame.transform.scale(self.image, size)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def set_blink_frequency(self, frequency):
        self.blinker.frequency = frequency

    def update(self):
        if self.visible:
            self.blinker.blink()
            self.draw()

    def draw(self):
        self.display_surface.blit(self.image, self.rect)

    def erase(self):
        self.parent.clear(self.old_rect)
