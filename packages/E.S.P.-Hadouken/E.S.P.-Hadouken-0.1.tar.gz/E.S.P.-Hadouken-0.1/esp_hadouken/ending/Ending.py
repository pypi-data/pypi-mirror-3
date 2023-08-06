from pygame import Surface, image

from esp_hadouken.GameChild import *
from esp_hadouken.Input import *
from esp_hadouken.Toy import *
from Score import *
from name_prompt.NamePrompt import *
from InputMessage import *
from esp_hadouken.scoreboard.Scoreboard import *

class Ending(GameChild, Surface):

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.display_surface = self.get_screen()
        Surface.__init__(self, self.display_surface.get_size())
        self.add_children()
        self.subscribe_to_events()
        self.set_background()
        self.deactivate()

    def add_children(self):
        self.score = Score(self)
        self.name_prompt = NamePrompt(self)
        self.input_message = InputMessage(self)
        self.scoreboard = Scoreboard(self)

    def subscribe_to_events(self):
        self.subscribe_to(USEREVENT, self.display)
        self.subscribe_to(Input.command_event, self.run_command)

    def display(self, evt=None):
        if not evt or evt.name == "toy-collected":
            self.deactivate()
            self.activate()
            self.activate_initial_widgets()
            self.update()

    def activate(self):
        self.active = True
        self.start_music()

    def activate_initial_widgets(self):
        self.input_message.activate()
        self.name_prompt.activate()
        self.score.activate()

    def deactivate(self):
        self.active = False
        self.deactivate_initial_widgets()
        self.scoreboard.deactivate()

    def deactivate_initial_widgets(self):
        self.input_message.deactivate()
        self.name_prompt.deactivate()
        self.score.deactivate()

    def run_command(self, evt):
        if evt.command == "reset":
            self.deactivate()
        if self.active and evt.command == "advance":
            if self.name_prompt.active:
                self.deactivate_initial_widgets()
                self.update()
                self.get_high_scores().add(self.name_prompt.get_initials())
                self.scoreboard.activate()
            else:
                self.get_input().post_command("reset")

    def set_background(self):
        path = self.get_resource("ending-bg-path")
        background = image.load(path).convert()
        self.background = background

    def set_toy(self):
        toy = Toy(self)
        config = self.get_configuration()
        toy.resize(config["ending-toy-size"])
        toy.place(config["ending-toy-position"])
        toy.show()
        self.toy = toy

    def start_music(self):
        path = self.get_resource("ending-audio-path")
        self.get_audio().play_bgm(path)

    def update(self):
        self.clear()
        self.score.update()
        self.name_prompt.update()
        self.input_message.update()
        self.scoreboard.update()
        self.draw()

    def clear(self):
        self.blit(self.background, (0, 0))

    def draw(self):
        self.display_surface.blit(self, (0, 0))
