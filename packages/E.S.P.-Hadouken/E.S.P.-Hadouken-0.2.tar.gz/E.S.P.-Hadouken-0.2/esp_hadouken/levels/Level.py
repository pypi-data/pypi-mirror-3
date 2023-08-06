from math import sqrt, pi, sin, cos
from random import random

from pygame import Surface, Rect, event, surfarray, image

from esp_hadouken.GameChild import *
from esp_hadouken.Input import *
from esp_hadouken.dot.Dot import *
from Bandit import *
from Void import *
from Exit import *
from Distance import *

class Level(GameChild, Surface):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.get_delegate().disable()
        self.get_input().suppress()
        self.init_surface()
        self.display_surface = self.get_screen()
        self.set_background()
        self.previous_displacement = (0, 0)
        self.rect = self.get_rect()
        self.add_children()
        self.set_max_target_distance()
        self.set_void()
        self.set_dot()
        self.set_bgm()
        self.reset()
        self.subscribe_to(Input.command_event, self.pause)
        self.get_delegate().enable()
        self.get_input().unsuppress()
        self.get_timer().start(self.get_name())

    def init_surface(self):
        size = self.get_configuration()[self.get_name() + "-level-dimensions"]
        Surface.__init__(self, size)

    def get_name(self):
        return self.__class__.__name__.lower()

    def set_background(self):
        bg = Surface(self.get_size())
        palette = self.build_bg_palette()
        checker_width = self.get_configuration()["level-checker-width"]
        for ii in range((self.get_width() / checker_width) + 1):
            for jj in range((self.get_height() / checker_width) + 1):
                index = (jj + ii) % len(palette)
                position = ii * checker_width, jj * checker_width
                dimensions = checker_width, checker_width
                bg.fill(palette[index], Rect(position, dimensions))
        self.background = bg.convert()

    def add_children(self):
        self.bandit = Bandit(self)
        self.exit = Exit(self)
        self.distance = Distance(self)

    def set_max_target_distance(self):
        target = self.bandit.rect.center
        max_target_distance = 0
        rect = self.get_rect()
        corners = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
        for corner in corners:
            distance = self.euclidean_distance(target, corner)
            if distance > max_target_distance:
                max_target_distance = distance
        self.max_target_distance = max_target_distance

    def euclidean_distance(self, p1, p2):
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def build_bg_palette(self):
        return map(Color,
                   self.get_configuration()[self.get_name() + "-level-palette"])

    def set_void(self):
        self.void = Void(self)

    def set_dot(self):
        bounds = None, (0, self.get_height())
        wrap = True, False
        dot = Dot(self, bounds, wrap)
        self.dot = dot
        self.set_dot_frequency()

    def get_blink_frequency_range(self):
        return self.get_configuration()["level-blink-frequency-range"]

    def set_dot_frequency(self):
        distance = self.get_distance_to_target()
        distance_ratio = 1 - (distance / self.max_target_distance)
        rnge = self.get_blink_frequency_range()
        frequency = distance_ratio * (rnge[1] - rnge[0]) + rnge[0]
        self.dot.set_blink_frequency(frequency)

    def get_distance_to_target(self):
        distance = self.dot.rect.top - self.bandit.rect.bottom
        if distance < 0:
            distance = 0
        return distance

    def set_bgm(self):
        path = self.get_resource("level-audio-path")
        self.get_audio().play_bgm(path, True)

    def reset(self):
        self.reset_dot()
        self.set_clip()
        self.paused = False

    def reset_dot(self):
        name = self.get_name()
        dot = self.dot
        dot.halt()
        dot.rect.center = self.get_configuration()[name + "-level-dot-position"]
        dot.show()

    def set_clip(self):
        rect = self.rect
        visible = Rect((-rect.left, -rect.top), self.display_surface.get_size())
        Surface.set_clip(self, visible)

    def pause(self, event):
        if event.command == "pause":
            self.get_audio().pause()
            self.get_timer().pause()
            self.get_pause_screen().show()
            self.paused = not self.paused

    def update(self):
        if not self.paused:
            self.dot.move([-val for val in self.previous_displacement])
            self.place()
            self.set_clip()
            self.clear()
            self.void.update()
            self.bandit.update()
            self.distance.update()
            self.displace_dot()
            self.dot.update()
            self.set_dot_frequency()
            self.collide_dot()
            self.draw()

    def displace_dot(self):
        angle = random() * pi * 2
        distance = self.get_distance_to_target()
        distance_ratio = 1 - (distance / self.max_target_distance)
        displacement = distance_ratio * self.get_max_dot_displacement()
        x = round(sin(angle) * displacement)
        y = round(cos(angle) * displacement)
        self.dot.move(x, y)
        self.previous_displacement = x, y

    def get_max_dot_displacement(self):
        return self.get_configuration()["level-max-dot-displacement"]

    def place(self):
        dot = self.dot.rect
        size = self.display_surface.get_size()
        pos = [-dot.centerx + size[0] / 2, -dot.centery + size[1] / 2]
        min_x = size[0] - self.get_width()
        if pos[0] < min_x:
            pos[0] = min_x
        elif pos[0] > 0:
            pos[0] = 0
        min_y = size[1] - self.get_height()
        if pos[1] < min_y:
            pos[1] = min_y
        elif pos[1] > 0:
            pos[1] = 0
        self.rect.topleft = pos

    def collide_dot(self):
        self.collide_dot_with_bandit()
        self.collide_dot_with_void()
        self.collide_dot_with_exit()

    def collide_dot_with_bandit(self):
        if self.dot.rect.colliderect(self.bandit.rect):
            self.get_audio().play_fx("drill")
            self.parent.clear_level()
            event.post(event.Event(USEREVENT, name="level-complete",
                                   bandit_name=self.get_name()))

    def collide_dot_with_void(self):
        dot = self.dot
        rect = dot.rect
        surfar = surfarray.pixels2d(self.void)
        for x, y in dot.outline:
            if not surfar[x + rect.left][y + rect.top]:
                self.get_audio().play_fx("tub")
                self.reset()
        del surfar

    def collide_dot_with_exit(self):
        if self.dot.rect.colliderect(self.exit.rect):
            self.get_audio().play_fx("Ag")
            self.parent.clear_level()
            event.post(event.Event(USEREVENT, name="level-exited"))

    def clear(self):
        self.blit(self.background, self.get_clip(), self.get_clip())

    def draw(self):
        self.exit.draw()
        self.display_surface.blit(self, self.rect)

    def end(self):
        self.get_timer().stop()
        self.unsubscribe_from_events()

    def unsubscribe_from_events(self):
        self.unsubscribe_from(Input.command_event, self.pause)
