from pygame import Surface, image, event
from pygame.locals import *

from esp_hadouken.GameChild import *
from esp_hadouken.Input import *
from esp_hadouken.Toy import *
from esp_hadouken.dot.Dot import *
from Bandits import *
from Wall import *

class Overworld(Surface, GameChild):

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.display_surface = self.get_screen()
        Surface.__init__(self, self.display_surface.get_size())
        self.deactivate()
        self.set_background()
        self.set_dot()
        self.set_toy()
        self.set_wall()
        self.bandits = Bandits(self)
        self.subscribe_to_events()
        self.reset()

    def set_background(self):
        path = self.get_resource("overworld-bg-path")
        self.background = image.load(path).convert()

    def set_dot(self):
        bounds = None, (0, self.get_height())
        wrap = True, False
        self.dot = Dot(self, bounds, wrap)

    def set_toy(self):
        toy = Toy(self)
        y = self.get_configuration()["overworld-toy-y"]
        toy.place(self.get_width() / 2 - toy.rect.w / 2, y)
        toy.show()
        self.toy = toy

    def set_wall(self):
        wall = Wall(self)
        wall.show()
        self.dot.add_restricted_areas(wall.get_rects())
        self.wall = wall

    def subscribe_to_events(self):
        self.subscribe_to(USEREVENT, self.respond_to_event)
        self.subscribe_to(Input.command_event, self.run_command)

    def reset(self):
        self.reset_dot()
        self.bandits.reset()
        self.paused = False

    def start_music(self):
        path = self.get_resource("overworld-audio-path")
        self.get_audio().play_bgm(path)

    def reset_dot(self):
        dot = self.dot
        y = self.get_configuration()["overworld-dot-y"]
        dot.place(self.get_width() / 2 - dot.rect.w / 2, y)
        dot.halt()
        dot.show()

    def respond_to_event(self, event):
        name = event.name
        if name == "intro-deactivated":
            self.activate()
        elif name in ["level-exited", "level-complete"]:
            self.activate()
            if name == "level-complete":
                self.bandits.remove(event.bandit_name)

    def activate(self):
        self.get_delegate().disable()
        self.active = True
        self.start_music()
        self.reset_dot()
        self.get_delegate().enable()

    def run_command(self, evt):
        if evt.command == "reset":
            self.reset()
            self.deactivate()
        elif evt.command == "pause" and self.active:
            self.pause()

    def pause(self):
        self.get_audio().pause()
        self.get_pause_screen().show()
        self.paused = not self.paused

    def deactivate(self):
        self.active = False

    def update(self):
        if self.active and not self.paused:
            self.clear()
            self.toy.update()
            self.wall.update()
            self.bandits.update()
            self.dot.update()
            self.collide_dot()
            self.draw()

    def collide_dot(self):
        dot = self.dot
        for bandit in self.bandits:
            if bandit.visible and dot.rect.colliderect(bandit.rect):
                dot.halt()
                self.get_audio().play_fx("Ag")
                self.deactivate()
                event.post(event.Event(USEREVENT, name="bandit-encountered",
                                       bandit=bandit))
        if dot.rect.colliderect(self.toy.rect):
            dot.halt()
            self.deactivate()
            event.post(event.Event(USEREVENT, name="toy-collected"))

    def draw(self):
        self.display_surface.blit(self, (0, 0))

    def clear(self):
        self.blit(self.background, (0, 0))
