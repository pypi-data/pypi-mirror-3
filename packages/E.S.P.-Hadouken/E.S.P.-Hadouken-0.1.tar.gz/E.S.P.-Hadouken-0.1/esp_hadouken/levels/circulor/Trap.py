from math import pi, sin, cos
from random import random, randint

from pygame import time, draw, Rect

from esp_hadouken import levels

class Trap(levels.Void.Void):

    def __init__(self, parent):
        levels.Void.Void.__init__(self, parent)
        self.read_configuration()
        self.reset()

    def read_configuration(self):
        config = self.get_configuration()
        prefix = "circulor-level-"
        self.radius_range = config[prefix + "radius-range"]
        self.trap_duration = config[prefix + "trap-duration"]
        self.speed = config[prefix + "speed"]
        self.thickness = config[prefix + "trap-thickness"]

    def reset(self):
        self.center = None
        self.total_elapsed = 0
        self.last_ticks = time.get_ticks()
        self.angle = random() * pi * 2

    def update_area(self):
        if self.parent.trapped:
            self.place()
            self.collide()
            if self.total_elapsed >= self.trap_duration:
                self.parent.trapped = False
                self.parent.escaped = True
            else:
                self.update_total_elapsed()
            self.draw_circle()

    def place(self):
        center = self.get_center()
        x_del, y_del = self.calculate_deltas()
        self.center = center[0] + x_del, center[1] + y_del

    def get_center(self):
        center = self.center
        if not center:
            center = self.parent.dot.rect.center
        return center

    def calculate_deltas(self):
        ang, distance = self.angle, self.speed
        return sin(ang) * distance, cos(ang) * distance

    def collide(self):
        angle = self.angle
        x, y = self.center
        radius = self.get_radius()
        rect = Rect(x - radius, y - radius, radius * 2, radius * 2)
        bandit = self.parent.bandit.rect
        if rect.colliderect(bandit):
            if bandit.left - rect.right > rect.top - bandit.bottom:
                angle = -angle
                rect.right = bandit.left
            else:
                angle = pi - angle
                rect.top = bandit.bottom
        field = self.parent.rect
        if rect.right > field.w or rect.left < 0:
            angle = -angle
            if rect.right > field.w:
                rect.right = field.w
            else:
                rect.left = 0
        if rect.top < 0 or rect.bottom > field.h:
            angle = pi - angle
            if rect.top < 0:
                rect.top = 0
            else:
                rect.bottom = field.h
        self.angle = angle
        self.center = rect.center

    def update_total_elapsed(self):
        current_ticks = time.get_ticks()
        self.total_elapsed += current_ticks - self.last_ticks
        self.last_ticks = current_ticks

    def draw_circle(self):
        center = tuple(map(int, self.center))
        color = self.opaque_color
        draw.circle(self, color, center, self.get_radius(), self.thickness)

    def get_radius(self):
        radius_r = self.radius_range
        pos = float(self.total_elapsed) / self.trap_duration
        return int(pos * (radius_r[1] - radius_r[0]) + radius_r[0])
