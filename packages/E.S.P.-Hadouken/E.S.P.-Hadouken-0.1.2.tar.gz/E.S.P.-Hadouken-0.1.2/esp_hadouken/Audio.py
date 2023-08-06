from os import listdir
from os.path import join

from pygame.mixer import Channel, Sound, music

from GameChild import *
from Input import *

class Audio(GameChild):

    current_channel = None
    paused = False
    muted = False

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.load_fx()
        self.subscribe_to(Input.command_event, self.mute)

    def load_fx(self):
        fx = {}
        root = self.get_resource("sfx-path")
        for name in listdir(root):
            fx[name.split(".")[0]] = Sound(join(root, name))
        self.fx = fx

    def mute(self, event):
        if event.command == "mute":
            self.muted = not self.muted
            self.set_volume()

    def set_volume(self):
        volume = int(not self.muted)
        music.set_volume(volume)
        if self.current_channel:
            self.current_channel.set_volume(volume)

    def play_bgm(self, path, stream=False):
        self.stop_current_channel()
        if stream:
            music.load(path)
            music.play(-1)
        else:
            self.current_channel = Sound(path).play(-1)
        self.set_volume()

    def stop_current_channel(self):
        music.stop()
        if self.current_channel:
            self.current_channel.stop()
        self.current_channel = None
        self.paused = False

    def play_fx(self, name):
        if not self.muted:
            self.fx[name].play()

    def pause(self):
        channel = self.current_channel
        paused = self.paused
        if paused:
            music.unpause()
            if channel:
                channel.unpause()
        else:
            music.pause()
            if channel:
                channel.pause()
        self.paused = not paused
