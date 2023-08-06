from pygame.locals import *

from esp_hadouken.GameChild import *
from esp_hadouken.Input import *
from octo.Octo import *
from diortem.Diortem import *
from circulor.Circulor import *
from horse.Horse import *
from tooth.Tooth import *

class LevelFactory(GameChild):

    level = None

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.subscribe_to_events()

    def subscribe_to_events(self):
        self.subscribe_to(USEREVENT, self.load_level)
        self.subscribe_to(Input.command_event, self.clear_level)

    def load_level(self, evt):
        if evt.name == "bandit-encountered":
            bandit = evt.bandit
            self.level = globals()[bandit.name.capitalize()](self)

    def clear_level(self, evt=None):
        if not evt or evt.command == "reset":
            if self.level:
                self.level.end()
            self.level = None

    def update(self):
        if self.level:
            self.level.update()
