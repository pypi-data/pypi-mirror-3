import sys

import pygame
from pygame import mouse, display, key
from pygame.locals import *

from GameChild import *
from Animation import *
from Audio import *
from Display import *
from Configuration import *
from EventDelegate import *
from Input import *
from ScreenGrabber import *
from Timer import *
from PauseScreen import *
from introduction.Introduction import *
from overworld.Overworld import *
from levels.LevelFactory import *
from ending.Ending import *
from scoreboard.HighScores import *
from scoreboard.GlyphPalette import *

class Game(GameChild, Animation):
    
    def __init__(self):
        GameChild.__init__(self)
        self.configuration = Configuration()
        Animation.__init__(self, self.configuration["display-frame-duration"])
        pygame.init()
        mouse.set_visible(False)
        self.add_children()
        self.subscribe_to_events()
        self.introduction.activate()
        self.clear_queue()
        self.delegate.enable()

    def add_children(self):
        self.display = Display(self)
        self.delegate = EventDelegate(self)
        self.input = Input(self)
        self.audio = Audio(self)
        self.screen_grabber = ScreenGrabber(self)
        self.timer = Timer(self)
        self.pause_screen = PauseScreen(self)
        self.introduction = Introduction(self)
        self.overworld = Overworld(self)
        self.level_factory = LevelFactory(self)
        self.glyph_palette = GlyphPalette(self)
        self.ending = Ending(self)
        self.high_scores = HighScores(self)

    def subscribe_to_events(self):
        self.subscribe_to(QUIT, self.end)
        self.subscribe_to(Input.command_event, self.end)

    def get_configuration(self):
        return self.configuration

    def get_input(self):
        return self.input

    def sequence(self):
        self.delegate.dispatch_events()
        self.introduction.update()
        self.overworld.update()
        self.level_factory.update()
        display.update()

    def end(self, evt):
        if evt.type == QUIT or evt.command == "quit":
            sys.exit()
        elif evt.command == "skip" and key.get_mods() & KMOD_LSHIFT:
            self.skip_to_ending()

    def skip_to_ending(self):
        self.timer.conceal()
        self.introduction.deactivate()
        self.ending.display()
