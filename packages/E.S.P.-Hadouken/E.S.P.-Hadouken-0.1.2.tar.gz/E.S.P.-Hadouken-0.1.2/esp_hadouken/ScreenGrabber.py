import os
import time

from pygame import image

from GameChild import *
from Input import *

class ScreenGrabber(GameChild):

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.subscribe_to(Input.command_event, self.save_display)

    def save_display(self, event):
        if event.command == "capture-screen":
            directory = self.get_configuration()["screen-capture-save-dir"]
            if not os.path.exists(directory):
                os.mkdir(directory)
            name = time.ctime().replace(" ", "-") + ".png"
            path = os.path.join(directory, name)
            capture = image.save(self.get_screen(), path)
