from os.path import exists, join, basename
from sys import argv

from pygame import mixer

import Game

class GameChild:

    def __init__(self, parent=None):
        self.parent = parent

    def get_game(self):
        current = self
        while not isinstance(current, Game.Game):
            current = current.parent
        return current

    def get_configuration(self):
        return self.get_game().get_configuration()

    def get_input(self):
        return self.get_game().get_input()

    def get_screen(self):
        return self.get_game().display.get_screen()

    def get_timer(self):
        return self.get_game().timer

    def get_audio(self):
        return self.get_game().audio

    def get_delegate(self):
        return self.get_game().delegate

    def get_resource(self, key):
        config = self.get_configuration()
        path = config[key]
        installed_path = join(config["resources-install-path"], path)
        if exists(installed_path) and self.use_installed_resource():
            return installed_path
        elif exists(path):
            return path
        return None

    def use_installed_resource(self):
        if "-l" in argv:
            return False
        return True

    def get_pause_screen(self):
        return self.get_game().pause_screen

    def get_high_scores(self):
        return self.get_game().high_scores

    def get_glyph_palette(self):
        return self.get_game().glyph_palette

    def subscribe_to(self, kind, callback):
        self.get_game().delegate.add_subscriber(kind, callback)

    def unsubscribe_from(self, kind, callback):
        self.get_game().delegate.remove_subscriber(kind, callback)

    def is_debug_mode(self):
        return "-d" in argv
