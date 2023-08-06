from pygame import image, Color

from esp_hadouken.GameChild import *
from esp_hadouken.Font import *

class Score(GameChild):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.pos = self.get_configuration()["ending-plate-position"]
        self.set_plate()

    def set_plate(self):
        path = self.get_resource("ending-plate-path")
        self.plate = image.load(path).convert_alpha()

    def render_score(self):
        config = self.get_configuration()
        color = Color(config["ending-score-color"])
        size = config["ending-score-size"]
        score = Font(self, size).render(self.build_text(), True, color)
        rect = score.get_rect()
        rect.center = self.plate.get_rect().center
        self.plate.blit(score, rect)

    def build_text(self):
        return "%i:%02i" % divmod(int(self.get_timer().total()), 60)

    def update(self):
        if self.active:
            self.set_plate()
            self.render_score()
            self.draw()

    def draw(self):
        self.parent.blit(self.plate, self.pos)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
