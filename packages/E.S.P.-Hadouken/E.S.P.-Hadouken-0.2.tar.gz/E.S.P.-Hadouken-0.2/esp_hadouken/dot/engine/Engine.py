import pygame
from math import cos, ceil, floor

from esp_hadouken.GameChild import *
from Vector import *

class Engine(GameChild):

    direction_count = 8
    (n, ne, e, se, s, sw, w, nw) = range(direction_count)

    def __init__(self, vehicle, magnitude):
        GameChild.__init__(self, vehicle)
        self.magnitude = magnitude
        self.thrusting = False
        self.add_vectors()

    def add_vectors(self):
        vectors = []
        for ii in range(self.direction_count):
            vectors.append(Vector(ii))
        self.vectors = vectors

    def update(self):
        direction = self.determine_direction()
        if direction is not None:
            self.vectors[direction].grow(self.magnitude)

    def determine_direction(self):
        axes = self.get_input().get_axes()
        if axes["up"] and axes["down"]:
            (axes["up"], axes["down"]) = (False, False)
        if axes["right"] and axes["left"]:
            (axes["right"], axes["left"]) = (False, False)
        if axes["up"]:
            if axes["right"]:
                return self.ne
            if axes["left"]:
                return self.nw
            return self.n
        if axes["right"]:
            if axes["down"]:
                return self.se
            return self.e
        if axes["down"]:
            if axes["left"]:
                return self.sw
            return self.s
        if axes["left"]:
            return self.w
        return None

    def calculate_offset(self):
        x, y = 0, 0
        for vector in self.vectors:
            magnitude, si, co = vector.magnitude, vector.sin, vector.cos
            x += magnitude * si
            y -= magnitude * co
        offset = map(lambda x: 0 if x < .1 and x > -.1 else x, (x, y))
        offset = self.accommodate_boundaries(offset)
        return self.avoid_restricted_areas(offset)

    def accommodate_boundaries(self, offset):
        sprite = self.parent
        x_bounds, y_bounds = sprite.bounds
        dims = sprite.rect.size
        next_x, next_y = self.calculate_next_position(offset)
        scope = self.find_breached_boundary_y(next_y)
        if scope:
            self.halt(self.e, self.w)
            if next_y < scope[0]:
                offset[1] += scope[0] - next_y
            else:
                offset[1] -= next_y + dims[1] - scope[1]
        scope = self.find_breached_boundary_x(next_x)
        if scope:
            self.halt(self.n, self.s)
            if next_x < scope[0]:
                offset[0] += scope[0] - next_x
            else:
                offset[0] -= next_x + dims[0] - scope[1]
        return offset

    def calculate_next_position(self, offset):
        pos = self.parent.rect.topleft
        offset = [ceil(x) if x > 0 else floor(x) for x in offset]
        return pos[0] + offset[0], pos[1] + offset[1]

    def find_breached_boundary_y(self, y):
        sprite = self.parent
        bounds = sprite.bounds[1]
        if bounds:
            lower, upper = bounds
            size = sprite.rect.size
            if lower is not None and y < lower:
                return bounds
            if upper is not None and y + size[1] > upper:
                return bounds
        return None

    def find_breached_boundary_x(self, x):
        sprite = self.parent
        bounds = sprite.bounds[0]
        if bounds:
            lower, upper = bounds
            size = sprite.rect.size
            if lower is not None and x < lower:
                return bounds
            if upper is not None and x + size[0] > upper:
                return bounds
        return None

    def halt(self, *args):
        for direction in args:
            self.absorb_diagonal_momentum(direction)
        for ii, vector in enumerate(self.vectors):
            if ii not in args:
                vector.cancel()

    def absorb_diagonal_momentum(self, direction):
        if direction == self.n:
            self.transfer_momentum(self.ne, self.n)
            self.transfer_momentum(self.nw, self.n)
        elif direction == self.e:
            self.transfer_momentum(self.ne, self.e)
            self.transfer_momentum(self.se, self.e)
        elif direction == self.s:
            self.transfer_momentum(self.se, self.s)
            self.transfer_momentum(self.sw, self.s)
        elif direction == self.w:
            self.transfer_momentum(self.sw, self.w)
            self.transfer_momentum(self.nw, self.w)

    def transfer_momentum(self, a, b):
        vectors = self.vectors
        sender = vectors[a]
        vectors[b].grow(abs(cos(sender.angle) * sender.magnitude))

    def avoid_restricted_areas(self, offset):
        sprite = self.parent
        rect = sprite.rect
        next_x, next_y = self.calculate_next_position(offset)
        for area in sprite.restricted_areas:
            if self.will_collide(area, offset):
                if rect.top > area.bottom or rect.bottom < area.top:
                    self.halt(self.e, self.w)
                    if rect.top > area.bottom:
                        offset[1] = area.bottom - rect.top + 1
                    else:
                        offset[1] = area.top - rect.bottom - 1
                elif rect.left > area.right or rect.right < area.left:
                    self.halt(self.n, self.s)
                    if rect.left > area.right:
                        offset[0] = area.right - rect.left + 1
                    else:
                        offset[0] = area.left - rect.right - 1
        return offset

    def will_collide(self, area, offset):
        x, y = self.calculate_next_position(offset)
        rect = self.parent.rect
        return y + rect.h >= area.top and x <= area.right and y <= area.bottom \
               and x + rect.w >= area.left
