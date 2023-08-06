from pygame.locals import *
from pygame import Surface, event, image, time, mixer

from esp_hadouken.Input import Input
from esp_hadouken.GameChild import *
from esp_hadouken.Toy import *
from esp_hadouken.Diortem import *
from esp_hadouken.Font import *
from Controls import *

class Introduction(Surface, GameChild):

    events = {
        "steal" : USEREVENT + 1,
        "turn" : USEREVENT + 2,
        "exit" : USEREVENT + 3,
        "prompt" : USEREVENT + 4,
        "reset" : USEREVENT + 5
        }
    flipped = False

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.display_surface = self.parent.display.get_screen()
        Surface.__init__(self, self.display_surface.get_size())
        self.active = False
        self.set_background()
        self.set_prompt()
        self.set_children()
        self.subscribe_to_events()

    def set_background(self):
        path = self.get_resource("introduction-bg-path")
        self.background = image.load(path).convert()

    def set_prompt(self):
        config = self.get_configuration()
        text = config["introduction-prompt-text"]
        color = Color(config["introduction-prompt-color"])
        size = config["introduction-prompt-size"]
        ttf = self.get_resource("font-path")
        self.prompt = Font(self, size).render(text, True, color)

    def set_children(self):
        self.toy = Toy(self)
        self.diortem = Diortem(self)
        self.controls = Controls(self)

    def subscribe_to_events(self):
        events = self.events
        self.subscribe_to(Input.command_event, self.run_command)
        self.subscribe_to(events["steal"], self.steal_toy)
        self.subscribe_to(events["turn"], self.turn_around)
        self.subscribe_to(events["exit"], self.walk_away)
        self.subscribe_to(events["prompt"], self.show_prompt)
        self.subscribe_to(events["reset"], self.reset)

    def activate(self):
        self.reset()
        self.active = True
        self.start_music()

    def start_music(self):
        path = self.get_resource("introduction-audio-path")
        self.get_audio().play_bgm(path)

    def deactivate(self):
        self.active = False

    def run_command(self, evt):
        if self.is_debug_mode():
            print "Introduction received %s, active = %s" % (evt.command,
                                                             self.active)
        if evt.command == "advance" and self.active:
            self.deactivate()
            event.post(event.Event(USEREVENT, name="intro-deactivated"))
        elif evt.command == "reset":
            self.activate()

    def reset(self, event=None):
        time.set_timer(self.events["reset"], 0)
        self.clear()
        self.reset_toy()
        self.reset_diortem()
        self.props_collided = False
        self.diortem_exited = False
        self.prompt_visible = False
        if self.flipped:
            self.flip_props()

    def reset_toy(self):
        toy = self.toy
        toy.show()
        toy.place(self.get_configuration()["introduction-toy-position"])
        self.toy_speed = 0

    def reset_diortem(self):
        diortem = self.diortem
        diortem.show()
        x = -diortem.rect.w - 100
        y = self.get_configuration()["introduction-diortem-y"]
        diortem.place(x, y)
        self.diortem_speed = \
            self.get_configuration()["introduction-entrance-speed"]

    def steal_toy(self, event):
        time.set_timer(self.events["steal"], 0)
        self.toy.move(-10, -25)
        time.set_timer(self.events["turn"], 1500)

    def turn_around(self, event):
        time.set_timer(self.events["turn"], 0)
        self.flip_props()
        self.toy.move(-56)
        time.set_timer(self.events["exit"], 1000)

    def flip_props(self):
        self.diortem.flip()
        self.toy.flip()
        self.flipped = not self.flipped

    def walk_away(self, event):
        time.set_timer(self.events["exit"], 0)
        speed = -self.get_configuration()["introduction-exit-speed"]
        self.diortem_speed = speed
        self.toy_speed = speed

    def show_prompt(self, event):
        time.set_timer(self.events["prompt"], 0)
        self.prompt_visible = True
        time.set_timer(self.events["reset"], 25000)

    def update(self):
        if self.active:
            self.clear()
            self.collide_props()
            self.check_for_exit()
            diortem, toy = self.diortem, self.toy
            diortem.move(self.diortem_speed)
            diortem.update()
            toy.move(self.toy_speed)
            toy.update()
            self.controls.draw()
            self.draw_prompt()
            self.draw()

    def collide_props(self):
        if not self.props_collided:
            if self.diortem.rect.colliderect(self.toy.rect):
                self.diortem_speed = 0
                time.set_timer(self.events["steal"], 1000)
                self.props_collided = True

    def check_for_exit(self):
        if self.props_collided and not self.diortem_exited:
            diortem = self.diortem
            if diortem.rect.right < 0:
                self.diortem_speed = 0
                self.toy_speed = 0
                self.flip_props()
                time.set_timer(self.events["prompt"], 2000)
                self.diortem_exited = True

    def draw_prompt(self):
        if self.prompt_visible:
            pos = self.get_configuration()["introduction-prompt-position"]
            self.blit(self.prompt, pos)

    def draw(self):
        self.display_surface.blit(self, (0, 0))

    def clear(self):
        self.blit(self.background, (0, 0))
